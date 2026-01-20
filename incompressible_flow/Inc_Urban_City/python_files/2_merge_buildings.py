"""
Merge touching buildings and keep only outer contours.
Removes internal contours that are enclosed by merged buildings.
"""

import pickle
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union, transform
from typing import Dict, List, Tuple
import pyproj


def load_building_polygons(filename: str) -> Dict[int, List[Tuple[float, float]]]:
    """Load building polygons from pickle file."""
    print(f"Loading building polygons from {filename}...")
    with open(filename, 'rb') as f:
        polygons = pickle.load(f)
    print(f"Loaded {len(polygons)} buildings")
    return polygons


def convert_to_shapely_polygons(polygon_dict: Dict[int, List[Tuple[float, float]]]) -> List[Polygon]:
    """Convert coordinate lists to Shapely Polygon objects."""
    print("Converting to Shapely polygons...")
    shapely_polygons = []

    for idx, coords in polygon_dict.items():
        try:
            # Handle MultiPolygon case (list of lists)
            if isinstance(coords[0], list):
                # This is a MultiPolygon - process each part
                for part_coords in coords:
                    if len(part_coords) >= 4:
                        poly = Polygon(part_coords)
                        if poly.is_valid and not poly.is_empty:
                            shapely_polygons.append(poly)
            else:
                # This is a simple Polygon
                if len(coords) >= 4:
                    poly = Polygon(coords)
                    if poly.is_valid and not poly.is_empty:
                        shapely_polygons.append(poly)
        except Exception as e:
            print(f"Warning: Skipping invalid polygon {idx}: {e}")
            continue

    print(f"Converted {len(shapely_polygons)} valid polygons")
    return shapely_polygons


def merge_touching_buildings(polygons: List[Polygon]) -> List[Polygon]:
    """
    Merge all buildings that are touching each other.
    Returns list of merged building polygons.
    """
    print("\nMerging touching buildings...")
    print(f"Input: {len(polygons)} buildings")

    # Use unary_union to merge all touching/overlapping polygons
    merged = unary_union(polygons)

    # Handle result - could be Polygon or MultiPolygon
    if isinstance(merged, Polygon):
        result = [merged]
    elif isinstance(merged, MultiPolygon):
        result = list(merged.geoms)
    else:
        result = []

    print(f"Output: {len(result)} merged buildings")
    return result


def extract_outer_contours_only(polygons: List[Polygon]) -> List[Polygon]:
    """
    Extract only outer contours, removing any interior holes.
    """
    print("\nExtracting outer contours only (removing interior holes)...")

    outer_only = []
    holes_removed = 0

    for poly in polygons:
        if isinstance(poly, Polygon):
            # Count interior holes
            num_holes = len(poly.interiors)
            if num_holes > 0:
                holes_removed += num_holes
                # Create new polygon with only exterior coordinates
                outer_poly = Polygon(poly.exterior.coords)
                outer_only.append(outer_poly)
            else:
                outer_only.append(poly)
        elif isinstance(poly, MultiPolygon):
            # Process each part of MultiPolygon
            for part in poly.geoms:
                num_holes = len(part.interiors)
                if num_holes > 0:
                    holes_removed += num_holes
                outer_poly = Polygon(part.exterior.coords)
                outer_only.append(outer_poly)

    print(f"Removed {holes_removed} interior holes/contours")
    print(f"Result: {len(outer_only)} buildings with outer contours only")
    return outer_only


def save_merged_polygons(polygons: List[Polygon], output_file: str) -> Dict[int, List[Tuple[float, float]]]:
    """
    Save merged polygons to pickle file in same format as input.
    """
    print(f"\nSaving merged polygons to {output_file}...")

    # Convert back to dictionary format
    polygon_dict = {}
    for idx, poly in enumerate(polygons):
        coords = list(poly.exterior.coords)
        polygon_dict[idx] = coords

    with open(output_file, 'wb') as f:
        pickle.dump(polygon_dict, f)

    print(f"Saved {len(polygon_dict)} merged buildings")
    return polygon_dict


def remove_small_touching_buildings(polygons: List[Polygon]) -> List[Polygon]:
    """
    Remove buildings that are touching/almost-touching if one is < 10% area of the other.
    Returns filtered list of polygons.
    """
    print("\n" + "=" * 60)
    print("FILTERING SMALL TOUCHING BUILDINGS")
    print("=" * 60)

    # First convert to metric for accurate distance calculation
    sample_coords = list(polygons[0].exterior.coords)[0]
    is_latlon = abs(sample_coords[0]) < 180 and abs(sample_coords[1]) < 90

    if is_latlon:
        print("Converting to metric coordinates for distance calculation...")
        wgs84 = pyproj.CRS('EPSG:4326')
        utm31n = pyproj.CRS('EPSG:32631')
        project = pyproj.Transformer.from_crs(wgs84, utm31n, always_xy=True).transform

        metric_polygons = []
        for poly in polygons:
            metric_poly = transform(project, poly)
            metric_polygons.append(metric_poly)
    else:
        metric_polygons = polygons

    num_polygons = len(polygons)
    buildings_to_remove = set()

    print(f"Analyzing {num_polygons} buildings for touching pairs...")

    # Find touching/almost-touching pairs
    for i in range(num_polygons):
        if i in buildings_to_remove:
            continue

        for j in range(i + 1, num_polygons):
            if j in buildings_to_remove:
                continue

            poly1 = metric_polygons[i]
            poly2 = metric_polygons[j]

            distance = poly1.distance(poly2)

            # Check if touching or almost touching (< 1cm)
            if distance < 0.01:
                area1 = poly1.area
                area2 = poly2.area

                # Check if one is < 10% of the other
                if area1 < area2:
                    ratio = area1 / area2
                    if ratio < 0.1:
                        buildings_to_remove.add(i)
                        print(f"  Removing building {i} (area: {area1:.2f} m², {ratio*100:.1f}% of building {j})")
                        break  # Move to next i
                else:
                    ratio = area2 / area1
                    if ratio < 0.1:
                        buildings_to_remove.add(j)
                        print(f"  Removing building {j} (area: {area2:.2f} m², {ratio*100:.1f}% of building {i})")

    # Create filtered list
    filtered_polygons = [poly for idx, poly in enumerate(polygons) if idx not in buildings_to_remove]

    print(f"\nRemoved {len(buildings_to_remove)} buildings: {sorted(buildings_to_remove)}")
    print(f"Remaining buildings: {len(filtered_polygons)}")
    print("=" * 60)

    return filtered_polygons


def merge_close_buildings_with_buffer(polygons: List[Polygon], buffer_distance: float = 1.0,
                                       merge_threshold: float = 0.002) -> List[Polygon]:
    """
    Merge buildings that are touching or very close using buffer-union-buffer method.

    Args:
        polygons: List of building polygons (in lat/lon coordinates)
        buffer_distance: Buffer size in meters for dilation/erosion (default 1.0m)
        merge_threshold: Distance threshold in meters for merging (default 2mm)

    Returns:
        List of merged polygons with touching buildings combined
    """
    print("\n" + "=" * 60)
    print("MERGING CLOSE BUILDINGS (Buffer-Union-Buffer Method)")
    print("=" * 60)
    print(f"Buffer distance: {buffer_distance} m")
    print(f"Merge threshold: {merge_threshold*1000:.1f} mm")

    # Convert to metric for accurate operations
    sample_coords = list(polygons[0].exterior.coords)[0]
    is_latlon = abs(sample_coords[0]) < 180 and abs(sample_coords[1]) < 90

    if is_latlon:
        print("\nConverting to metric coordinates (UTM)...")
        wgs84 = pyproj.CRS('EPSG:4326')
        utm31n = pyproj.CRS('EPSG:32631')
        project_to_utm = pyproj.Transformer.from_crs(wgs84, utm31n, always_xy=True).transform
        project_to_wgs = pyproj.Transformer.from_crs(utm31n, wgs84, always_xy=True).transform

        metric_polygons = [transform(project_to_utm, poly) for poly in polygons]
    else:
        metric_polygons = polygons
        project_to_wgs = None

    # Find groups of buildings to merge
    num_polygons = len(metric_polygons)
    merge_groups = []  # List of sets of indices to merge
    processed = set()

    print(f"\nAnalyzing {num_polygons} buildings for close pairs...")

    for i in range(num_polygons):
        if i in processed:
            continue

        # Start a new group with this building
        group = {i}
        queue = [i]

        while queue:
            current = queue.pop(0)
            current_poly = metric_polygons[current]

            # Check all other buildings
            for j in range(num_polygons):
                if j in group or j in processed:
                    continue

                other_poly = metric_polygons[j]
                distance = current_poly.distance(other_poly)

                # If close enough, add to group
                if distance <= merge_threshold:
                    group.add(j)
                    queue.append(j)

        if len(group) > 1:
            merge_groups.append(group)
            processed.update(group)
            print(f"  Found merge group: buildings {sorted(group)} (distances ≤ {merge_threshold*1000:.1f} mm)")

    print(f"\nFound {len(merge_groups)} groups to merge")

    # Perform merging
    result_polygons = []
    merged_indices = set()

    for group in merge_groups:
        group_polys = [metric_polygons[i] for i in group]

        # Apply buffer-union-buffer method
        # Step 1: Buffer (dilate) to connect close buildings
        buffered = [poly.buffer(buffer_distance) for poly in group_polys]

        # Step 2: Union to merge
        merged = unary_union(buffered)

        # Step 3: Negative buffer (erode) to restore approximate size
        result = merged.buffer(-buffer_distance)

        # Handle MultiPolygon result
        if isinstance(result, MultiPolygon):
            for geom in result.geoms:
                if geom.is_valid and geom.area > 1.0:  # Skip very small artifacts
                    result_polygons.append(geom)
        elif isinstance(result, Polygon) and result.is_valid and result.area > 1.0:
            result_polygons.append(result)

        merged_indices.update(group)

        # Report merge
        areas = [metric_polygons[i].area for i in group]
        merged_area = result.area if isinstance(result, Polygon) else sum(g.area for g in result.geoms)
        print(f"  Merged buildings {sorted(group)}: {sum(areas):.2f} m² → {merged_area:.2f} m²")

    # Add unmerged buildings
    for i in range(num_polygons):
        if i not in merged_indices:
            result_polygons.append(metric_polygons[i])

    print(f"\nResult: {len(result_polygons)} buildings ({num_polygons} → {len(result_polygons)})")

    # Convert back to lat/lon if needed
    if is_latlon:
        print("Converting back to lat/lon coordinates...")
        result_polygons = [transform(project_to_wgs, poly) for poly in result_polygons]

    print("=" * 60)

    return result_polygons


def check_overlaps_and_distances(polygons: List[Polygon]):
    """
    Check for overlaps between buildings and calculate minimum distances.
    Reports warnings for any overlaps and the smallest distance found.
    NOTE: Polygons must be in metric coordinates for accurate distance calculation.
    """
    print("\n" + "=" * 60)
    print("OVERLAP AND DISTANCE ANALYSIS")
    print("=" * 60)

    num_polygons = len(polygons)

    # Check for duplicate polygons
    print(f"Checking for duplicate polygons...")
    duplicates = []
    for i in range(num_polygons):
        for j in range(i + 1, num_polygons):
            if polygons[i].equals(polygons[j]):
                duplicates.append((i, j))

    if duplicates:
        print(f"  ⚠ WARNING: Found {len(duplicates)} duplicate polygon pairs:")
        for i, j in duplicates[:10]:
            print(f"    Polygons {i} and {j} are identical")
        if len(duplicates) > 10:
            print(f"    ... and {len(duplicates) - 10} more")
    else:
        print(f"  ✓ No duplicate polygons found")

    # First, check if coordinates are in lat/lon or meters by examining magnitude
    sample_coords = list(polygons[0].exterior.coords)[0]
    is_latlon = abs(sample_coords[0]) < 180 and abs(sample_coords[1]) < 90

    if is_latlon:
        print(f"\n⚠ WARNING: Coordinates appear to be in lat/lon (degrees)")
        print(f"  Sample coordinate: ({sample_coords[0]:.6f}, {sample_coords[1]:.6f})")
        print(f"  Converting to metric coordinates (UTM) for accurate distance calculation...")

        # Convert to UTM zone 31N (Amsterdam)
        wgs84 = pyproj.CRS('EPSG:4326')
        utm31n = pyproj.CRS('EPSG:32631')
        project = pyproj.Transformer.from_crs(wgs84, utm31n, always_xy=True).transform

        # Convert all polygons to metric coordinates
        metric_polygons = []
        for poly in polygons:
            metric_poly = transform(project, poly)
            metric_polygons.append(metric_poly)

        print(f"  ✓ Converted {len(metric_polygons)} polygons to UTM coordinates")
        polygons_to_check = metric_polygons
    else:
        print(f"\nℹ Coordinates appear to be in metric system")
        print(f"  Sample coordinate: ({sample_coords[0]:.2f}, {sample_coords[1]:.2f})")
        polygons_to_check = polygons

    overlaps = []
    min_distance = float('inf')
    min_distance_pair = None
    close_pairs = []  # Buildings closer than 2m
    touching_pairs = []  # Buildings with distance < 0.01m

    print(f"\nChecking {num_polygons} buildings for overlaps...")

    # Check all pairs of buildings
    for i in range(num_polygons):
        for j in range(i + 1, num_polygons):
            poly1 = polygons_to_check[i]
            poly2 = polygons_to_check[j]

            # Check for overlap
            if poly1.intersects(poly2):
                intersection = poly1.intersection(poly2)
                # Only count as overlap if it's more than just touching (has area)
                if hasattr(intersection, 'area') and intersection.area > 1e-6:
                    overlaps.append((i, j, intersection.area))
                    print(f"⚠ WARNING: Buildings {i} and {j} overlap! Area: {intersection.area:.6f}")

            # Calculate distance between buildings
            distance = poly1.distance(poly2)
            if distance < min_distance:
                min_distance = distance
                min_distance_pair = (i, j)

            # Track close buildings (in meters)
            if distance < 0.01:
                touching_pairs.append((i, j, distance))
            elif distance < 2.0:
                close_pairs.append((i, j, distance))

    # Report results
    print(f"\nOverlap check complete:")
    if overlaps:
        print(f"  ❌ Found {len(overlaps)} overlapping building pairs!")
        total_overlap_area = sum(area for _, _, area in overlaps)
        print(f"  Total overlap area: {total_overlap_area:.6f}")
        print(f"\nOverlapping pairs:")
        for i, j, area in overlaps:
            print(f"    Buildings {i} <-> {j}: overlap area = {area:.6f}")
    else:
        print(f"  ✓ No overlaps detected - all buildings are properly separated")

    print(f"\nDistance analysis:")
    if min_distance_pair:
        i, j = min_distance_pair
        print(f"  Minimum distance: {min_distance:.6f} meters")
        print(f"  Between buildings {i} and {j}")

        # Report touching buildings
        if touching_pairs:
            print(f"\n  ⚠ WARNING: Found {len(touching_pairs)} touching/nearly-touching pairs (< 1cm):")
            for i, j, dist in sorted(touching_pairs, key=lambda x: x[2])[:10]:  # Show top 10
                print(f"    Buildings {i} <-> {j}: distance = {dist:.6f} m")
            if len(touching_pairs) > 10:
                print(f"    ... and {len(touching_pairs) - 10} more")
            print(f"  ⚠ These may cause meshing issues!")

        # Report close buildings
        if close_pairs:
            print(f"\n  ℹ INFO: Found {len(close_pairs)} close pairs (< 2m):")
            for i, j, dist in sorted(close_pairs, key=lambda x: x[2])[:5]:  # Show top 5
                print(f"    Buildings {i} <-> {j}: distance = {dist:.6f} m")
            if len(close_pairs) > 5:
                print(f"    ... and {len(close_pairs) - 5} more")

    print("=" * 60)

    return len(overlaps) == 0, min_distance, len(touching_pairs), len(close_pairs)


def print_statistics(original_polygons: List[Polygon], merged_polygons: List[Polygon]):
    """Print statistics about the merge operation."""
    print("\n" + "=" * 60)
    print("MERGE STATISTICS")
    print("=" * 60)
    print(f"Original buildings:        {len(original_polygons)}")
    print(f"Merged buildings:          {len(merged_polygons)}")
    print(f"Reduction:                 {len(original_polygons) - len(merged_polygons)} buildings")
    print(f"Reduction percentage:      {100 * (1 - len(merged_polygons)/len(original_polygons)):.1f}%")

    # Calculate total area
    original_area = sum(p.area for p in original_polygons)
    merged_area = sum(p.area for p in merged_polygons)

    print(f"\nOriginal total area:       {original_area:.6f}")
    print(f"Merged total area:         {merged_area:.6f}")
    print(f"Area difference:           {abs(original_area - merged_area):.6f} ({100*abs(original_area - merged_area)/original_area:.2f}%)")
    print("=" * 60)


def main():
    """Main execution function."""
    input_file = "amsterdam_building_polygons.pkl"
    output_file = "amsterdam_merged_buildings.pkl"

    print("=" * 60)
    print("BUILDING MERGER - Merge Touching Buildings")
    print("=" * 60)

    # Load polygons
    polygon_dict = load_building_polygons(input_file)

    # Convert to Shapely
    shapely_polygons = convert_to_shapely_polygons(polygon_dict)

    if not shapely_polygons:
        print("Error: No valid polygons to process")
        return

    # Merge touching buildings
    merged_polygons = merge_touching_buildings(shapely_polygons)

    # Remove interior holes
    final_polygons = extract_outer_contours_only(merged_polygons)

    # Remove small buildings that are touching larger ones
    filtered_polygons = remove_small_touching_buildings(final_polygons)

    # Merge remaining close buildings using buffer-union-buffer method
    final_merged_polygons = merge_close_buildings_with_buffer(
        filtered_polygons,
        buffer_distance=1.0,      # 1 meter buffer for merging
        merge_threshold=0.1     # Merge buildings within 10cm
    )

    # Save result
    result_dict = save_merged_polygons(final_merged_polygons, output_file)

    # Print statistics
    print_statistics(shapely_polygons, final_merged_polygons)

    # Check for overlaps and calculate distances
    no_overlaps, min_dist, num_touching, num_close = check_overlaps_and_distances(final_merged_polygons)

    print(f"\n✓ Merging complete!")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")

    if not no_overlaps:
        print(f"\n⚠ WARNING: Overlaps detected! Consider reviewing the merged buildings.")
    else:
        print(f"\n✓ Quality check passed: No overlaps detected")
        print(f"  Minimum distance between buildings: {min_dist:.3f} meters")
        if num_touching > 0:
            print(f"  ⚠ {num_touching} touching/nearly-touching pairs detected - may cause mesh issues")
        if num_close > 0:
            print(f"  ℹ {num_close} close pairs (< 2m) detected")


if __name__ == "__main__":
    main()
