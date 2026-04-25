#!/usr/bin/env python3
"""
Simplify and smooth building contours using combined Douglas-Peucker + dilation-erosion.
Reads amsterdam_merged_buildings.pkl and produces simplified buildings.
"""

import pickle
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import transform
import pyproj
from typing import Dict, List, Tuple


def load_building_polygons(filename: str) -> Dict[int, List[Tuple[float, float]]]:
    """Load building polygons from pickle file."""
    print(f"Loading buildings from {filename}...")
    with open(filename, 'rb') as f:
        polygon_dict = pickle.load(f)
    print(f"Loaded {len(polygon_dict)} buildings")
    return polygon_dict


def convert_to_shapely_polygons(polygon_dict: Dict[int, List[Tuple[float, float]]]) -> List[Polygon]:
    """Convert coordinate lists to Shapely Polygon objects."""
    print("Converting to Shapely polygons...")
    shapely_polygons = []

    for idx, coords in polygon_dict.items():
        try:
            if len(coords) >= 4:
                poly = Polygon(coords)
                if poly.is_valid and not poly.is_empty:
                    shapely_polygons.append(poly)
        except Exception as e:
            print(f"Warning: Skipping invalid polygon {idx}: {e}")
            continue

    print(f"Converted {len(shapely_polygons)} valid polygons")
    return shapely_polygons


def simplify_and_smooth_buildings(polygons: List[Polygon],
                                   simplify_tolerance: float = 0.5,
                                   dilation_size: float = 0.8,
                                   erosion_size: float = 1.0) -> List[Polygon]:
    """
    Simplify and smooth building contours using combined approach.

    Args:
        polygons: List of building polygons in lat/lon
        simplify_tolerance: Douglas-Peucker tolerance in meters
        dilation_size: Buffer size for dilation in meters
        erosion_size: Buffer size for erosion in meters (should be > dilation_size)

    Returns:
        List of simplified and smoothed polygons
    """
    print("\n" + "=" * 60)
    print("SIMPLIFYING AND SMOOTHING BUILDINGS")
    print("=" * 60)
    print(f"Method: Dilation-Erosion + Douglas-Peucker (Combined)")
    print(f"Parameters:")
    print(f"  - Simplification tolerance: {simplify_tolerance} m")
    print(f"  - Dilation (buffer +): {dilation_size} m")
    print(f"  - Erosion (buffer -): {erosion_size} m")
    print(f"  - Net effect: -{erosion_size - dilation_size:.2f} m (creates separation)")

    # Coordinates are already in meters
    print(f"\nProcessing {len(polygons)} buildings...")
    metric_polygons = polygons

    # Statistics tracking
    original_vertices = sum(len(poly.exterior.coords) for poly in metric_polygons)
    original_area = sum(poly.area for poly in metric_polygons)

    simplified_polygons = []
    removed_holes_count = 0

    for idx, poly in enumerate(metric_polygons):
        try:
            # Step 1: Dilation (expand, smooth corners)
            dilated = poly.buffer(dilation_size)

            # Step 2: Erosion (shrink back)
            eroded = dilated.buffer(-erosion_size)

            # Step 3: Douglas-Peucker simplification (reduce vertex density of smooth shape)
            simplified = eroded.simplify(simplify_tolerance, preserve_topology=True)

            # Handle result (can be Polygon, MultiPolygon, or empty)
            if isinstance(simplified, Polygon):
                if simplified.is_valid and simplified.area > 1.0:  # Skip tiny artifacts
                    # Remove internal holes/contours created by dilation
                    num_holes = len(simplified.interiors)
                    if num_holes > 0:
                        removed_holes_count += num_holes
                        # Keep only outer contour
                        outer_only = Polygon(simplified.exterior.coords)
                        simplified_polygons.append(outer_only)
                    else:
                        simplified_polygons.append(simplified)
            elif isinstance(simplified, MultiPolygon):
                # Take only the largest polygon from MultiPolygon
                largest = max(simplified.geoms, key=lambda p: p.area)
                if largest.area > 1.0:
                    # Remove internal holes
                    num_holes = len(largest.interiors)
                    if num_holes > 0:
                        removed_holes_count += num_holes
                    outer_only = Polygon(largest.exterior.coords)
                    simplified_polygons.append(outer_only)
            # If result is empty or invalid, skip this building

        except Exception as e:
            print(f"Warning: Error processing building {idx}: {e}")
            continue

    # Calculate statistics
    final_vertices = sum(len(poly.exterior.coords) for poly in simplified_polygons)
    final_area = sum(poly.area for poly in simplified_polygons)

    print(f"\n" + "=" * 60)
    print("SIMPLIFICATION RESULTS")
    print("=" * 60)
    print(f"Buildings: {len(metric_polygons)} → {len(simplified_polygons)}")
    print(f"Vertices: {original_vertices} → {final_vertices} ({100*(1-final_vertices/original_vertices):.1f}% reduction)")
    print(f"Area: {original_area:.2f} m² → {final_area:.2f} m² ({100*(final_area/original_area-1):.2f}% change)")
    print(f"Internal holes removed: {removed_holes_count}")
    print("=" * 60)

    return simplified_polygons


def filter_small_polygons(polygons: List[Polygon], min_area_m2: float = 25.0) -> List[Polygon]:
    """
    Remove polygons smaller than the minimum area threshold.

    Args:
        polygons: List of building polygons (in metric coordinates)
        min_area_m2: Minimum area in square meters

    Returns:
        List of filtered polygons
    """
    print("\n" + "=" * 60)
    print("FILTERING SMALL CONTOURS")
    print("=" * 60)
    print(f"Minimum area threshold: {min_area_m2} m²")

    # Separate into kept and removed
    kept_polygons = []
    removed_polygons = []
    removed_areas = []

    for poly in polygons:
        area = poly.area
        if area >= min_area_m2:
            kept_polygons.append(poly)
        else:
            removed_polygons.append(poly)
            removed_areas.append(area)

    # Print statistics
    print(f"\nBuildings kept: {len(kept_polygons)}")
    print(f"Buildings removed: {len(removed_polygons)}")

    if removed_areas:
        print(f"\nRemoved contour areas (m²):")
        removed_areas_sorted = sorted(removed_areas, reverse=True)
        for i, area in enumerate(removed_areas_sorted, 1):
            print(f"  {i:2d}. {area:7.2f} m²")
        print(f"\nTotal area removed: {sum(removed_areas):.2f} m²")
        print(f"Average removed area: {sum(removed_areas)/len(removed_areas):.2f} m²")
        print(f"Smallest removed: {min(removed_areas):.2f} m²")
        print(f"Largest removed: {max(removed_areas):.2f} m²")
    else:
        print("\nNo contours removed (all above threshold)")

    print("=" * 60)

    return kept_polygons


def analyze_edge_lengths(polygons: List[Polygon], min_edge_threshold: float = 1.0) -> None:
    """
    Analyze edge lengths in building contours to detect remaining small features.

    Args:
        polygons: List of building polygons (in metric coordinates)
        min_edge_threshold: Report edges shorter than this length (meters)
    """
    print("\n" + "=" * 60)
    print("ANALYZING EDGE LENGTHS")
    print("=" * 60)
    print(f"Checking for edges shorter than {min_edge_threshold} m...")

    all_edges = []
    small_edges = []
    buildings_with_small_edges = []

    for idx, poly in enumerate(polygons):
        coords = list(poly.exterior.coords)
        building_small_edges = []

        # Calculate edge lengths
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            edge_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            all_edges.append(edge_length)

            if edge_length < min_edge_threshold:
                small_edges.append(edge_length)
                building_small_edges.append(edge_length)

        if building_small_edges:
            buildings_with_small_edges.append({
                'building_idx': idx,
                'num_small_edges': len(building_small_edges),
                'min_edge': min(building_small_edges),
                'max_edge': max(building_small_edges),
                'avg_edge': sum(building_small_edges) / len(building_small_edges)
            })

    # Overall statistics
    print(f"\nTotal edges analyzed: {len(all_edges)}")
    print(f"Total buildings: {len(polygons)}")

    if all_edges:
        print(f"\nAll edges statistics:")
        print(f"  Shortest edge: {min(all_edges):.3f} m")
        print(f"  Longest edge: {max(all_edges):.3f} m")
        print(f"  Average edge: {sum(all_edges)/len(all_edges):.3f} m")
        print(f"  Median edge: {sorted(all_edges)[len(all_edges)//2]:.3f} m")

    # Small edges statistics
    if small_edges:
        print(f"\nSmall edges (< {min_edge_threshold} m):")
        print(f"  Count: {len(small_edges)} ({100*len(small_edges)/len(all_edges):.2f}% of all edges)")
        print(f"  Shortest: {min(small_edges):.3f} m")
        print(f"  Longest: {max(small_edges):.3f} m")
        print(f"  Average: {sum(small_edges)/len(small_edges):.3f} m")

        print(f"\nBuildings with small edges: {len(buildings_with_small_edges)} ({100*len(buildings_with_small_edges)/len(polygons):.1f}%)")

        if len(buildings_with_small_edges) > 0:
            print(f"\nTop 10 buildings with most small edges:")
            sorted_buildings = sorted(buildings_with_small_edges,
                                     key=lambda x: x['num_small_edges'],
                                     reverse=True)[:10]
            for i, bldg in enumerate(sorted_buildings, 1):
                print(f"  {i:2d}. Building {bldg['building_idx']:3d}: "
                      f"{bldg['num_small_edges']:3d} small edges, "
                      f"min={bldg['min_edge']:.3f}m, "
                      f"max={bldg['max_edge']:.3f}m, "
                      f"avg={bldg['avg_edge']:.3f}m")
    else:
        print(f"\n✓ No edges shorter than {min_edge_threshold} m found!")
        print(f"  All contours are well-defeatured.")

    print("=" * 60)


def save_polygons(polygons: List[Polygon], output_file: str) -> Dict[int, List[Tuple[float, float]]]:
    """Save polygons to pickle file in dictionary format (coordinates already in meters, centered at origin)."""
    print(f"\nSaving to {output_file} (coordinates in meters, centered at origin)...")

    # Calculate minimum edge size
    all_edge_lengths = []
    for poly in polygons:
        coords = list(poly.exterior.coords)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            edge_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            all_edge_lengths.append(edge_length)

    min_edge_size = min(all_edge_lengths) if all_edge_lengths else 0.0

    # Calculate minimum separation distance between buildings
    print("  Computing minimum separation distance between buildings...")
    min_separation = float('inf')
    n_buildings = len(polygons)

    for i in range(n_buildings):
        for j in range(i + 1, n_buildings):
            distance = polygons[i].distance(polygons[j])
            if distance < min_separation:
                min_separation = distance

    if min_separation == float('inf'):
        min_separation = 0.0  # Only one building or no buildings

    # Convert to dictionary format
    polygon_dict = {}
    for idx, poly in enumerate(polygons):
        coords = list(poly.exterior.coords)
        polygon_dict[idx] = coords

    with open(output_file, 'wb') as f:
        pickle.dump(polygon_dict, f)

    print(f"Saved {len(polygon_dict)} buildings")
    print(f"  Minimum edge size: {min_edge_size:.3f} m")
    print(f"  Minimum separation distance: {min_separation:.3f} m")
    return polygon_dict


def main():
    """Main execution function."""
    input_file = "amsterdam_merged_buildings.pkl"
    output_file = "amsterdam_simplified_buildings.pkl"

    print("=" * 60)
    print("BUILDING SIMPLIFICATION AND SMOOTHING")
    print("=" * 60)

    # Load buildings
    polygon_dict = load_building_polygons(input_file)

    # Convert to Shapely
    polygons = convert_to_shapely_polygons(polygon_dict)

    if not polygons:
        print("Error: No valid polygons to process")
        return

    # =========================================================================
    # SMOOTHING PARAMETERS - Adjust these to control defeaturing level
    # =========================================================================
    #
    # simplify_tolerance: Douglas-Peucker algorithm removes vertices within
    #   this distance from the simplified line.
    #   - INCREASE (e.g., 1.0-2.0) for MORE smoothing/defeaturing
    #   - DECREASE (e.g., 0.2-0.3) for LESS smoothing (preserves detail)
    #
    # dilation_size: Expands building outward (rounds corners).
    #   - INCREASE (e.g., 1.5-3.0) for SMOOTHER, more rounded corners
    #   - DECREASE (e.g., 0.3-0.5) for LESS rounding (sharper corners)
    #
    # erosion_size: Shrinks building inward after dilation.
    #   - Should be EQUAL or SLIGHTLY LARGER than dilation_size
    #   - Equal values (erosion = dilation): smooth corners, no net size change
    #   - Larger erosion: creates separation between buildings
    #   - IMPORTANT: simplify_tolerance should be SMALLER than dilation/erosion
    #     to preserve the smooth curves created by buffering
    #
    # Example settings:
    #   Conservative (less smoothing):  dilation=0.5, erosion=0.7, tolerance=0.1
    #   Moderate (balanced):            dilation=1.5, erosion=1.5, tolerance=0.3
    #   Aggressive (maximum smoothing): dilation=3.0, erosion=3.0, tolerance=0.5
    # =========================================================================

    simplified_polygons = simplify_and_smooth_buildings(
        polygons,
        simplify_tolerance=0.5,    # Reduce vertex density after smoothing
        dilation_size=1.0,         # Large expansion to test smoothing effect
        erosion_size=1.0           # Equal to dilation (no net shrinkage)
    )

    # Filter small polygons (coordinates already in meters)
    print("\nFiltering small polygons...")
    filtered_polygons = filter_small_polygons(simplified_polygons, min_area_m2=25.0)

    # Analyze edge lengths to detect remaining small features
    analyze_edge_lengths(filtered_polygons, min_edge_threshold=1.0)

    # Save result
    save_polygons(filtered_polygons, output_file)

    print(f"\n{'='*60}")
    print("✓ Simplification complete!")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
