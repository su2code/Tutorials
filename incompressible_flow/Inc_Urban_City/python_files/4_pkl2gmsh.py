#!/usr/bin/env python3
"""
Generate gmsh mesh from simplified building contours.
Creates a 400m radius circular domain with buildings as holes (not meshed).
"""

import pickle
import numpy as np
import gmsh
from shapely.geometry import Polygon, Point, MultiPolygon
from typing import List, Tuple, Dict


def load_building_polygons(filename: str) -> Dict[int, List[Tuple[float, float]]]:
    """Load building polygons from pickle file (coordinates already in meters, centered at origin)."""
    print(f"Loading buildings from {filename}...")
    with open(filename, 'rb') as f:
        polygon_dict = pickle.load(f)
    print(f"✓ Loaded {len(polygon_dict)} buildings (coordinates in meters, centered at (0,0))")
    return polygon_dict


def convert_to_metric(polygon_dict: Dict[int, List[Tuple[float, float]]]) -> Tuple[List[Polygon], Tuple[float, float]]:
    """
    Convert building polygon dictionary to Shapely Polygon list.
    Coordinates are already in meters centered at (0,0).
    """
    print("\nConverting to Shapely polygons...")

    # Circle center is at origin since coordinates are pre-centered
    center = (0.0, 0.0)
    print(f"  Circle center: ({center[0]:.2f}, {center[1]:.2f}) m")

    # Convert coordinate lists to Polygon objects
    polygons_metric = []
    for idx, coords in polygon_dict.items():
        if len(coords) >= 4:
            poly = Polygon(coords)
            if poly.is_valid and not poly.is_empty:
                polygons_metric.append(poly)

    print(f"✓ Converted {len(polygons_metric)} polygons")
    return polygons_metric, center


def clip_polygons_to_circle(polygons: List[Polygon], center: Tuple[float, float], radius: float) -> List[Polygon]:
    """
    Clip building polygons to circle boundary.
    Buildings that cross the edge have their vertices densified for clean intersection.
    """
    print(f"\nClipping buildings to {radius}m radius circle...")

    # Create circle geometry
    circle = Point(center).buffer(radius)

    clipped_polygons = []
    buildings_removed = 0
    buildings_clipped = 0

    for poly in polygons:
        if poly.intersects(circle):
            # If building is not fully within circle, densify edges before clipping
            if not poly.within(circle):
                # Densify: add vertices every 0.5m along edges for smooth intersection
                coords = list(poly.exterior.coords)
                densified_coords = []

                for i in range(len(coords) - 1):
                    x1, y1 = coords[i]
                    x2, y2 = coords[i + 1]

                    # Add start point
                    densified_coords.append((x1, y1))

                    # Calculate edge length
                    edge_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                    # Add intermediate points every 0.5m
                    if edge_length > 0.5:
                        num_segments = int(np.ceil(edge_length / 0.5))
                        for j in range(1, num_segments):
                            t = j / num_segments
                            x_new = x1 + t * (x2 - x1)
                            y_new = y1 + t * (y2 - y1)
                            densified_coords.append((x_new, y_new))

                # Close the polygon
                densified_coords.append(coords[-1])
                poly = Polygon(densified_coords)
                buildings_clipped += 1

            clipped = poly.intersection(circle)

            # Handle different geometry types
            if isinstance(clipped, Polygon) and clipped.area > 1.0:
                # Remove interior holes for mesh simplicity
                outer_only = Polygon(clipped.exterior.coords)
                clipped_polygons.append(outer_only)
                if not poly.within(circle):
                    buildings_clipped += 1
            elif isinstance(clipped, MultiPolygon):
                # Take largest polygon
                largest = max(clipped.geoms, key=lambda p: p.area)
                if largest.area > 1.0:
                    outer_only = Polygon(largest.exterior.coords)
                    clipped_polygons.append(outer_only)
                    buildings_clipped += 1
        else:
            buildings_removed += 1

    print(f"  Buildings fully inside: {len(clipped_polygons) - buildings_clipped}")
    print(f"  Buildings clipped: {buildings_clipped}")
    print(f"  Buildings removed (outside): {buildings_removed}")
    print(f"✓ Result: {len(clipped_polygons)} buildings in domain")

    return clipped_polygons


def create_gmsh_mesh(buildings: List[Polygon], center: Tuple[float, float], radius: float,
                     mesh_size_building: float = 5.0, mesh_size_far: float = 10.0,
                     add_circle_layer: bool = False, circle_layer_width: float = 25.0,
                     refine_circle_center: Tuple[float, float] = None,
                     refine_circle_radius: float = None,
                     refine_mesh_size: float = None,
                     transition_distance: float = 50.0,
                     boundary_layer_first_height: float = 1.0,
                     boundary_layer_num_layers: int = 2,
                     boundary_layer_growth: float = 1.2,
                     mesh_size_min_factor: float = 0.25):
    """
    Create gmsh mesh with circular domain and buildings as holes.

    Args:
        buildings: List of building polygons in meters
        center: Circle center coordinates (x, y) in meters
        radius: Circle radius in meters
        mesh_size_building: Fine mesh size near buildings (meters)
        mesh_size_far: Coarse mesh size far from buildings (meters)
        add_circle_layer: If True, add an outer ring to connect streets (default: False)
        circle_layer_width: Width of the outer ring in meters (default: 25.0)
        refine_circle_center: Center (x, y) of circular refinement region (default: None)
        refine_circle_radius: Radius of circular refinement region in meters (default: None)
        refine_mesh_size: Mesh size in refinement region (default: None)
    """
    print("\n" + "=" * 70)
    print("GENERATING GMSH MESH")
    print("=" * 70)
    print(f"Parameters:")
    if add_circle_layer:
        print(f"  Domain: Circle with radius {radius + circle_layer_width} m centered at ({center[0]:.2f}, {center[1]:.2f})")
        print(f"  Inner circle (building cutoff): {radius} m")
        print(f"  Outer ring width: {circle_layer_width} m (connects streets)")
    else:
        print(f"  Domain: Circle with radius {radius} m centered at ({center[0]:.2f}, {center[1]:.2f})")
    print(f"  Buildings: {len(buildings)} (as holes - not meshed)")
    print(f"  Mesh size near buildings: {mesh_size_building} m")
    print(f"  Mesh size far from buildings: {mesh_size_far} m")
    if refine_circle_center is not None and refine_circle_radius is not None and refine_mesh_size is not None:
        print(f"  Refinement circle: center=({refine_circle_center[0]:.2f}, {refine_circle_center[1]:.2f}), radius={refine_circle_radius} m")
        print(f"  Refinement mesh size: {refine_mesh_size} m")

    gmsh.initialize()
    gmsh.model.add("amsterdam_mesh")

    # Use OpenCASCADE kernel for boolean operations
    factory = gmsh.model.occ

    try:
        # Create circular domain
        if add_circle_layer:
            print("\nCreating circular domain with outer ring...")
            # Create outer circle - this is the actual mesh domain
            circle_tag = factory.addDisk(center[0], center[1], 0, radius + circle_layer_width, radius + circle_layer_width)
            print(f"✓ Created domain circle (r={radius + circle_layer_width}m) with tag {circle_tag}")
            print(f"  Buildings will be cut at r={radius}m")
        else:
            print("\nCreating circular domain...")
            circle_tag = factory.addDisk(center[0], center[1], 0, radius, radius)
            print(f"✓ Created circle with tag {circle_tag}")

        # Synchronize to get the circle boundary curves before boolean operations
        factory.synchronize()

        # Get the boundary curves of the circle disk (these are the farfield boundary)
        circle_boundary = gmsh.model.getBoundary([(2, circle_tag)], oriented=False)
        circle_curve_tags = [abs(tag) for dim, tag in circle_boundary if dim == 1]
        print(f"  Circle boundary: {len(circle_curve_tags)} curve(s) with tags {circle_curve_tags}")

        # Create building holes with linear segments (robust, accurate boundaries)
        print(f"\nCreating {len(buildings)} building holes...")
        building_tags = []

        # If adding outer ring, clip buildings to inner radius first
        buildings_to_mesh = buildings
        if add_circle_layer:
            print(f"  Clipping buildings to r={radius}m...")
            from shapely.geometry import Point as ShapelyPoint
            inner_circle = ShapelyPoint(center).buffer(radius)
            clipped_buildings = []
            for building in buildings:
                if building.intersects(inner_circle):
                    clipped = building.intersection(inner_circle)
                    if isinstance(clipped, Polygon) and clipped.area > 1.0:
                        clipped_buildings.append(Polygon(clipped.exterior.coords))
                    elif isinstance(clipped, MultiPolygon):
                        for geom in clipped.geoms:
                            if geom.area > 1.0:
                                clipped_buildings.append(Polygon(geom.exterior.coords))
            buildings_to_mesh = clipped_buildings
            print(f"  {len(buildings_to_mesh)} buildings after clipping")

        for idx, building in enumerate(buildings_to_mesh):
            try:
                coords = list(building.exterior.coords)

                # Create points from building boundary
                point_tags = []
                for x, y in coords[:-1]:  # Skip last point (duplicate of first)
                    pt = factory.addPoint(x, y, 0)
                    point_tags.append(pt)

                # Create linear segments connecting points
                # This ensures accurate building boundaries without deformation
                line_tags = []
                for i in range(len(point_tags)):
                    next_i = (i + 1) % len(point_tags)
                    line = factory.addLine(point_tags[i], point_tags[next_i])
                    line_tags.append(line)

                # Create curve loop and surface
                # Create curve loop and surface
                curve_loop = factory.addCurveLoop(line_tags)
                surface = factory.addPlaneSurface([curve_loop])
                building_tags.append(surface)

                if (idx + 1) % 20 == 0:
                    print(f"  Progress: {idx + 1}/{len(buildings)} buildings created")

            except Exception as e:
                print(f"Warning: Failed to create building {idx}: {e}")
                continue

        print(f"✓ Created {len(building_tags)} building surfaces")

        # Cut buildings from circle domain
        print("\nPerforming boolean difference (circle - buildings)...")
        if building_tags:
            result = factory.cut(
                [(2, circle_tag)],
                [(2, tag) for tag in building_tags],
                removeObject=True,
                removeTool=True
            )
            print(f"✓ Boolean difference complete")
            if add_circle_layer:
                print(f"✓ Domain includes outer ring from r={radius}m to r={radius + circle_layer_width}m")
        else:
            print("Warning: No buildings to cut")

        # Synchronize CAD model
        print("\nSynchronizing geometry...")
        factory.synchronize()
        print("✓ Geometry synchronized")

        # Verify which circle curves still exist after boolean operations
        all_curves = gmsh.model.getEntities(1)
        existing_curve_tags = [tag for dim, tag in all_curves]

        # The original circle boundary curve was destroyed during boolean cut
        # Gmsh created a new Ellipse curve for the farfield boundary
        # Identify it by curve type (Ellipse vs Line for building edges)

        circle_curves = []
        building_curves = []

        for curve_tag in existing_curve_tags:
            # Get curve type
            curve_type = gmsh.model.getType(1, curve_tag)

            # Circle boundary is an Ellipse, building edges are Lines
            if curve_type == "Ellipse" or curve_type == "Circle":
                circle_curves.append(curve_tag)
            else:
                building_curves.append(curve_tag)

        print(f"  Curves after boolean: {len(existing_curve_tags)} total")
        print(f"  Original circle curve tags before cut: {circle_curve_tags} (destroyed)")
        print(f"  New curve tags range after cut: {min(existing_curve_tags)} to {max(existing_curve_tags)}")
        print(f"  Farfield curves identified (type Ellipse/Circle): {len(circle_curves)}")
        print(f"  Building curves (type Line): {len(building_curves)}")

        # Create physical groups for boundaries
        if building_curves:
            phys_building = gmsh.model.addPhysicalGroup(1, building_curves, name="wall_buildings")
            print(f"  Physical group 'wall_buildings': {len(building_curves)} curves (tag {phys_building})")

        if circle_curves:
            phys_farfield = gmsh.model.addPhysicalGroup(1, circle_curves, name="farfield")
            print(f"  Physical group 'farfield': {len(circle_curves)} curves (tag {phys_farfield})")

        # Add physical group for the 2D domain surface
        all_surfaces = gmsh.model.getEntities(2)
        if all_surfaces:
            surface_tags = [tag for dim, tag in all_surfaces]
            phys_domain = gmsh.model.addPhysicalGroup(2, surface_tags, name="domain")
            print(f"  Physical group 'domain': {len(surface_tags)} surface(s) (tag {phys_domain})")

        # Create distance field from building edges only (not circle)
        field_dist = 1
        gmsh.model.mesh.field.add("Distance", field_dist)
        # Use only building curves for distance field (exclude circle to avoid refinement at farfield)
        gmsh.model.mesh.field.setNumbers(field_dist, "CurvesList", building_curves)
        gmsh.model.mesh.field.setNumbers(field_dist, "PointsList", point_tags)

        # Create threshold field for smooth size transition
        # This controls the mesh size based on distance from buildings
        field_threshold = 2
        gmsh.model.mesh.field.add("Threshold", field_threshold)
        gmsh.model.mesh.field.setNumber(field_threshold, "InField", field_dist)
        gmsh.model.mesh.field.setNumber(field_threshold, "SizeMin", mesh_size_building)
        gmsh.model.mesh.field.setNumber(field_threshold, "SizeMax", mesh_size_far)
        gmsh.model.mesh.field.setNumber(field_threshold, "DistMin", 0.0)  # At building boundaries: fine mesh
        gmsh.model.mesh.field.setNumber(field_threshold, "DistMax", transition_distance)  # Transition distance to coarse mesh

        # Add circular refinement region if specified
        background_field = field_threshold
        if refine_circle_center is not None and refine_circle_radius is not None and refine_mesh_size is not None:
            # Create a point at the refinement circle center
            refine_point = factory.addPoint(refine_circle_center[0], refine_circle_center[1], 0)
            factory.synchronize()

            # Create distance field from refinement center point
            field_refine_dist = 3
            gmsh.model.mesh.field.add("Distance", field_refine_dist)
            gmsh.model.mesh.field.setNumbers(field_refine_dist, "PointsList", [refine_point])

            # Create threshold field for refinement circle
            field_refine_threshold = 4
            gmsh.model.mesh.field.add("Threshold", field_refine_threshold)
            gmsh.model.mesh.field.setNumber(field_refine_threshold, "InField", field_refine_dist)
            gmsh.model.mesh.field.setNumber(field_refine_threshold, "SizeMin", refine_mesh_size)
            gmsh.model.mesh.field.setNumber(field_refine_threshold, "SizeMax", mesh_size_far)  # Transition to coarse mesh outside
            gmsh.model.mesh.field.setNumber(field_refine_threshold, "DistMin", refine_circle_radius * 0.9)  # Keep fine mesh in inner 90% of circle
            gmsh.model.mesh.field.setNumber(field_refine_threshold, "DistMax", refine_circle_radius)  # Transition in outer 10%

            # Combine both fields using Min field
            field_min = 5
            gmsh.model.mesh.field.add("Min", field_min)
            gmsh.model.mesh.field.setNumbers(field_min, "FieldsList", [field_threshold, field_refine_threshold])
            background_field = field_min
            print(f"✓ Circular refinement region added at ({refine_circle_center[0]:.2f}, {refine_circle_center[1]:.2f}) with radius {refine_circle_radius}m")

        # Set as background field
        gmsh.model.mesh.field.setAsBackgroundMesh(background_field)

        # Set global mesh options for better control
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size_building * mesh_size_min_factor)  # Allow BL size
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_far)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)  # Don't use point sizes
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)  # Don't use curvature
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)  # Don't extend from boundary
        gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay for 2D

        print(f"✓ Mesh size field configured")

        # Generate 2D mesh
        print("\nGenerating 2D mesh...")
        gmsh.model.mesh.generate(2)
        print("✓ 2D mesh generated")

        # Add boundary layer (inflation layer) on building walls
        print("\nConfiguring boundary layer (inflation layer)...")
        if building_curves and boundary_layer_num_layers > 0 and boundary_layer_first_height > 0:
            boundary_layer_size = boundary_layer_first_height
            num_layers = boundary_layer_num_layers
            growth = boundary_layer_growth
            total_thickness = 1.05*boundary_layer_size * sum([growth**i for i in range(num_layers)])

            # Create boundary layer field (use ID 10 to avoid conflicts with refinement fields)
            field_bl = 10
            gmsh.model.mesh.field.add('BoundaryLayer', field_bl)
            gmsh.model.mesh.field.setNumbers(field_bl, 'CurvesList', building_curves)
            gmsh.model.mesh.field.setNumber(field_bl, 'Size', boundary_layer_size)
            gmsh.model.mesh.field.setNumber(field_bl, 'Ratio', growth)  # Growth ratio between layers
            gmsh.model.mesh.field.setNumber(field_bl, 'Quads', 1)  # Use quads for boundary layer
            gmsh.model.mesh.field.setNumber(field_bl, 'Thickness', total_thickness)

            # Set as boundary layer (not background mesh)
            gmsh.model.mesh.field.setAsBoundaryLayer(field_bl)

            # Regenerate mesh with boundary layer
            gmsh.model.mesh.clear()
            gmsh.model.mesh.generate(2)

            print(f"  Boundary layer: {num_layers} layers, {boundary_layer_size:.2f}m first layer thickness")
            print(f"  Total thickness: {total_thickness:.2f}m, growth ratio: {growth}")
            print(f"  Applied to {len(building_curves)} building curves")
        else:
            print("  Boundary layer disabled (set boundary_layer_num_layers > 0 to enable)")

        # Get mesh statistics
        nodes = gmsh.model.mesh.getNodes()
        elements = gmsh.model.mesh.getElements(dim=2)

        num_nodes = len(nodes[0])
        # elements[0] contains element types, elements[1] contains element tags arrays
        num_triangles = 0
        num_quads = 0
        for elem_type, elem_tags in zip(elements[0], elements[1]):
            if elem_type == 2:  # Triangle
                num_triangles = len(elem_tags)
            elif elem_type == 3:  # Quadrangle
                num_quads = len(elem_tags)

        print("\n" + "=" * 70)
        print("MESH STATISTICS")
        print("=" * 70)
        print(f"Nodes: {num_nodes}")
        print(f"Triangular elements: {num_triangles}")
        print(f"Quadrangular elements: {num_quads}")
        print("=" * 70)

        # Save mesh
        output_file = "amsterdam_mesh.msh"
        gmsh.write(output_file)
        print(f"\n✓ Mesh saved to {output_file}")

        # Optionally launch GUI
        # gmsh.fltk.run()

    except Exception as e:
        print(f"\n✗ Error during mesh generation: {e}")
        raise

    finally:
        gmsh.finalize()


def create_inverse_mesh(buildings: List[Polygon], center: Tuple[float, float], radius: float,
                        mesh_size_building: float = 5.0):
    """
    Create gmsh mesh of buildings only (inverse of the regular mesh).
    Meshes the interior of buildings instead of the spaces between them.

    Args:
        buildings: List of building polygons in meters
        center: Circle center coordinates (x, y) in meters
        radius: Circle radius in meters
        mesh_size_building: Mesh size for building interiors (meters)
    """
    print("\n" + "=" * 70)
    print("GENERATING INVERSE MESH (BUILDINGS ONLY)")
    print("=" * 70)
    print(f"Parameters:")
    print(f"  Domain: Buildings within {radius}m radius circle centered at ({center[0]:.2f}, {center[1]:.2f})")
    print(f"  Buildings: {len(buildings)} (meshed interiors)")
    print(f"  Mesh size: {mesh_size_building} m")

    gmsh.initialize()
    gmsh.model.add("amsterdam_inverse_mesh")

    # Use OpenCASCADE kernel for boolean operations
    factory = gmsh.model.occ

    try:
        # Create circle for clipping
        circle = Point(center).buffer(radius)

        # Clip buildings to circle and create surfaces
        print(f"\nCreating {len(buildings)} building surfaces...")
        building_surface_tags = []
        valid_buildings = 0

        for idx, building in enumerate(buildings):
            try:
                # Clip building to circle if needed
                if building.intersects(circle):
                    if not building.within(circle):
                        clipped = building.intersection(circle)
                        if isinstance(clipped, Polygon) and clipped.area > 1.0:
                            building = Polygon(clipped.exterior.coords)
                        elif isinstance(clipped, MultiPolygon):
                            building = max(clipped.geoms, key=lambda p: p.area)
                        else:
                            continue

                    coords = list(building.exterior.coords)

                    # Create points from building boundary
                    point_tags = []
                    for x, y in coords[:-1]:  # Skip last point (duplicate of first)
                        pt = factory.addPoint(x, y, 0)
                        point_tags.append(pt)

                    # Create linear segments connecting points
                    line_tags = []
                    for i in range(len(point_tags)):
                        next_i = (i + 1) % len(point_tags)
                        line = factory.addLine(point_tags[i], point_tags[next_i])
                        line_tags.append(line)

                    # Create curve loop and surface
                    curve_loop = factory.addCurveLoop(line_tags)
                    surface = factory.addPlaneSurface([curve_loop])
                    building_surface_tags.append(surface)
                    valid_buildings += 1

                    if (valid_buildings) % 20 == 0:
                        print(f"  Progress: {valid_buildings}/{len(buildings)} buildings created")

            except Exception as e:
                print(f"Warning: Failed to create building {idx}: {e}")
                continue

        print(f"✓ Created {len(building_surface_tags)} building surfaces")

        # Synchronize CAD model
        print("\nSynchronizing geometry...")
        factory.synchronize()
        print("✓ Geometry synchronized")

        # Get all curves (building boundaries)
        all_curves = gmsh.model.getEntities(1)
        building_boundary_curves = [tag for dim, tag in all_curves]

        # Create physical groups
        if building_boundary_curves:
            phys_building_walls = gmsh.model.addPhysicalGroup(1, building_boundary_curves, name="building_walls")
            print(f"  Physical group 'building_walls': {len(building_boundary_curves)} curves (tag {phys_building_walls})")

        if building_surface_tags:
            phys_buildings = gmsh.model.addPhysicalGroup(2, building_surface_tags, name="buildings")
            print(f"  Physical group 'buildings': {len(building_surface_tags)} surface(s) (tag {phys_buildings})")

        # Set mesh size
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size_building / 2)
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_building)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size_building / 2)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size_building)
        gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay for 2D

        print(f"✓ Mesh size configured: {mesh_size_building} m")

        # Generate 2D mesh
        print("\nGenerating 2D mesh for buildings...")
        gmsh.model.mesh.generate(2)
        print("✓ 2D mesh generated")

        # Get mesh statistics
        nodes = gmsh.model.mesh.getNodes()
        elements = gmsh.model.mesh.getElements(dim=2)

        num_nodes = len(nodes[0])
        num_triangles = 0
        num_quads = 0
        for elem_type, elem_tags in zip(elements[0], elements[1]):
            if elem_type == 2:  # Triangle
                num_triangles = len(elem_tags)
            elif elem_type == 3:  # Quadrangle
                num_quads = len(elem_tags)

        print("\n" + "=" * 70)
        print("INVERSE MESH STATISTICS")
        print("=" * 70)
        print(f"Nodes: {num_nodes}")
        print(f"Triangular elements: {num_triangles}")
        print(f"Quadrangular elements: {num_quads}")
        print(f"Buildings meshed: {len(building_surface_tags)}")
        print("=" * 70)

        # Save mesh
        output_file = "amsterdam_inverse.msh"
        gmsh.write(output_file)
        print(f"\n✓ Inverse mesh saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error during inverse mesh generation: {e}")
        raise

    finally:
        gmsh.finalize()


def main():
    """Main execution function."""
    print("=" * 70)
    print("AMSTERDAM MESH GENERATION")
    print("=" * 70)

    # ===== MESH SIZE PARAMETERS (USER DEFINED) =====
    # Main mesh sizing - coarse mesh
    #mesh_size_near = 1.0    # fine mesh near buildings and edges (meters)
    #mesh_size_far = 5.0    # coarse mesh far from buildings (meters)
    #transition_distance = 20.0  # distance over which mesh transitions from fine to coarse (meters)

    # Boundary layer (inflation layer) on building walls
    #boundary_layer_first_height = 0.2  # first layer thickness (meters) - set to 0 to disable
    #boundary_layer_num_layers = 2  # number of boundary layers - set to 0 to disable
    #boundary_layer_growth = 1.2  # growth ratio between layers

    # Main mesh sizing - medium mesh
    #mesh_size_near = 0.5    # fine mesh near buildings and edges (meters)
    #mesh_size_far = 2.5    # coarse mesh far from buildings (meters)
    #transition_distance = 15.0  # distance over which mesh transitions from fine to coarse (meters)

    # Boundary layer (inflation layer) on building walls
    #boundary_layer_first_height = 0.2  # first layer thickness (meters) - set to 0 to disable
    #boundary_layer_num_layers = 2  # number of boundary layers - set to 0 to disable
    #boundary_layer_growth = 1.2  # growth ratio between layers

    # Main mesh sizing
    #mesh_size_near = 0.3    # fine mesh near buildings and edges (meters)
    #mesh_size_far = 2.0    # coarse mesh far from buildings (meters)
    #transition_distance = 15.0  # distance over which mesh transitions from fine to coarse (meters)

    # Boundary layer (inflation layer) on building walls
    #boundary_layer_first_height = 0.04  # first layer thickness (meters) - set to 0 to disable
    #boundary_layer_num_layers = 3  # number of boundary layers - set to 0 to disable
    #boundary_layer_growth = 1.1  # growth ratio between layers

    # Main mesh sizing
    mesh_size_near = 0.2    # fine mesh near buildings and edges (meters)
    mesh_size_far = 2.0    # coarse mesh far from buildings (meters)
    transition_distance = 15.0  # distance over which mesh transitions from fine to coarse (meters)

    # Boundary layer (inflation layer) on building walls
    boundary_layer_first_height = 0.01  # first layer thickness (meters) - set to 0 to disable
    boundary_layer_num_layers = 5  # number of boundary layers - set to 0 to disable
    boundary_layer_growth = 1.1  # growth ratio between layers

    # Circular refinement region (optional, set refine_radius=None to disable)
    refine_x = 0.0
    refine_y = 0.0
    refine_radius = 5.0  # set to None to disable refinement region
    refine_size = 0.5  # mesh size in refinement region (meters)

    # Inverse mesh (building interiors)
    inverse_mesh_size = 2.0  # mesh size for building interiors (meters)

    # Global mesh options
    mesh_size_min_factor = 0.25  # minimum mesh size as fraction of mesh_size_near
    # ===============================================

    # Domain parameters
    input_file = "amsterdam_simplified_buildings.pkl"
    circle_radius = 400.0  # meters
    add_outer_ring = True  # Add outer ring to connect streets
    outer_ring_width = 100.0  # Width of outer ring in meters

    # Load buildings
    polygon_dict = load_building_polygons(input_file)

    if not polygon_dict:
        print("Error: No buildings loaded")
        return

    # Convert to metric coordinates
    buildings_metric, center_utm = convert_to_metric(polygon_dict)

    if not buildings_metric:
        print("Error: No valid buildings after conversion")
        return

    # Don't clip buildings here - let gmsh OpenCASCADE handle intersection
    print(f"\nPassing {len(buildings_metric)} buildings to gmsh for boolean intersection...")

    # Generate regular mesh (streets/spaces between buildings)
    create_gmsh_mesh(buildings_metric, center_utm, circle_radius,
                     mesh_size_building=mesh_size_near,
                     mesh_size_far=mesh_size_far,
                     add_circle_layer=add_outer_ring,
                     circle_layer_width=outer_ring_width,
                     refine_circle_center=(refine_x, refine_y) if refine_radius else None,
                     refine_circle_radius=refine_radius,
                     refine_mesh_size=refine_size,
                     transition_distance=transition_distance,
                     boundary_layer_first_height=boundary_layer_first_height,
                     boundary_layer_num_layers=boundary_layer_num_layers,
                     boundary_layer_growth=boundary_layer_growth,
                     mesh_size_min_factor=mesh_size_min_factor)

    print("\n" + "=" * 70)
    print("✓ REGULAR MESH GENERATION COMPLETE")
    print("=" * 70)

    # Generate inverse mesh (buildings only)
    #create_inverse_mesh(buildings_metric, center_utm, circle_radius,
    #                   mesh_size_building=inverse_mesh_size)

    print("\n" + "=" * 70)
    print("✓ ALL MESH GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
