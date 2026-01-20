"""
Download and visualize building footprints from OpenStreetMap.
Provides functions to fetch building data within a radius and create visualizations.
"""

from typing import Optional, Dict, List, Tuple, Any
import requests

# Optional imports for building visualization
try:
    import osmnx as ox
    import geopandas as gpd
    import folium
    import matplotlib.pyplot as plt
    from shapely.geometry import Point, Polygon, MultiPolygon
    from shapely.ops import transform
    import pyproj
    BUILDING_VIZ_AVAILABLE = True
except ImportError:
    BUILDING_VIZ_AVAILABLE = False


def get_buildings_in_radius(
    latitude: float,
    longitude: float,
    radius_meters: int = 1000,
    output_file: Optional[str] = None
) -> Optional[Any]:
    """
    Fetch building footprints from OpenStreetMap within a radius around coordinates.
    Uses direct Overpass API for faster retrieval of 2D building contours.

    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_meters: Radius in meters around the coordinates (default: 1000m = 1km)
        output_file: Optional path to save buildings as GeoJSON for QGIS (e.g., 'buildings.geojson')

    Returns:
        GeoDataFrame containing building footprints with geometries and attributes,
        or None if data cannot be retrieved

    Example:
        >>> buildings = get_buildings_in_radius(52.37, 4.89, radius_meters=1000)
        >>> print(f"Found {len(buildings)} buildings")
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        print("Install with: pip install osmnx geopandas folium")
        return None

    try:
        import time
        start_time = time.time()

        print(f"Fetching buildings within {radius_meters}m of ({latitude:.6f}, {longitude:.6f})...")
        print("Querying Overpass API...", end='', flush=True)

        # Use direct Overpass API query for faster retrieval
        # This gets building ways, relations, and buildings with special status
        overpass_url = "https://overpass-api.de/api/interpreter"

        overpass_query = f"""
        [out:json][timeout:60];
        (
          way["building"](around:{radius_meters},{latitude},{longitude});
          relation["building"](around:{radius_meters},{latitude},{longitude});
          way["building:part"](around:{radius_meters},{latitude},{longitude});
          relation["building:part"](around:{radius_meters},{latitude},{longitude});
        );
        out geom;
        """

        # Retry logic with exponential backoff for rate limiting
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                response = requests.post(overpass_url, data={'data': overpass_query}, timeout=90)
                response.raise_for_status()
                break  # Success, exit retry loop

            except requests.exceptions.HTTPError as e:
                if response.status_code in [429, 504, 503]:  # Rate limit or timeout
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"\nAPI overloaded (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...", end='', flush=True)
                        time.sleep(wait_time)
                    else:
                        raise  # Last attempt failed
                else:
                    raise  # Other HTTP error
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"\nTimeout (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...", end='', flush=True)
                    time.sleep(wait_time)
                else:
                    raise  # Last attempt failed

        elapsed = time.time() - start_time
        print(f" done ({elapsed:.1f}s)")
        print("Processing building data...", end='', flush=True)

        data = response.json()

        if 'elements' not in data or len(data['elements']) == 0:
            print(f"\nNo buildings found within {radius_meters}m radius")
            return None

        # Convert to GeoDataFrame
        buildings_list = []
        for element in data['elements']:
            try:
                poly = None

                # Handle ways (simple polygons)
                if element['type'] == 'way' and 'geometry' in element:
                    # Extract coordinates
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]

                    # Create polygon (close it if not closed)
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])

                    if len(coords) >= 4:  # Need at least 3 unique points + closing point
                        poly = Polygon(coords)

                # Handle relations (multi-part buildings)
                elif element['type'] == 'relation' and 'members' in element:
                    # Extract all outer ways from the relation
                    polygons = []
                    for member in element['members']:
                        if member.get('role') == 'outer' and 'geometry' in member:
                            member_coords = [(node['lon'], node['lat']) for node in member['geometry']]
                            if member_coords[0] != member_coords[-1]:
                                member_coords.append(member_coords[0])
                            if len(member_coords) >= 4:
                                polygons.append(Polygon(member_coords))

                    # Create MultiPolygon or single Polygon
                    if len(polygons) == 1:
                        poly = polygons[0]
                    elif len(polygons) > 1:
                        poly = MultiPolygon(polygons)

                # Add to list if we successfully created a geometry
                if poly is not None and not poly.is_empty:
                    # Extract building attributes
                    tags = element.get('tags', {})
                    building_data = {
                        'geometry': poly,
                        'osm_id': element.get('id'),
                        'building': tags.get('building') or tags.get('building:part', 'yes'),
                        'name': tags.get('name'),
                        'height': tags.get('height'),
                        'levels': tags.get('building:levels')
                    }
                    buildings_list.append(building_data)

            except Exception as e:
                # Skip malformed buildings
                continue

        if not buildings_list:
            print(f"\nNo valid buildings found")
            return None

        buildings = gpd.GeoDataFrame(buildings_list, crs='EPSG:4326')

        elapsed = time.time() - start_time
        print(f" done ({elapsed:.1f}s)")
        print(f"Found {len(buildings)} buildings (total time: {elapsed:.1f}s)")

        # Save to GeoJSON if output file specified
        if output_file:
            print(f"Saving to {output_file}...", end='', flush=True)
            buildings.to_file(output_file, driver='GeoJSON')
            print(f" done")

        return buildings

    except requests.exceptions.Timeout:
        print(f"\nTimeout: Query took too long after {max_retries} attempts. Try reducing the radius or try again later.")
        return None
    except requests.exceptions.HTTPError as e:
        if hasattr(e, 'response') and e.response.status_code in [429, 503, 504]:
            print(f"\nOverpass API is overloaded or rate-limited. Please wait a few minutes and try again.")
        else:
            print(f"\nHTTP error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nAPI request error: {e}")
        print("The Overpass API may be temporarily unavailable. Try again in a few minutes.")
        return None
    except Exception as e:
        print(f"\nError fetching building data: {e}")
        return None


def save_buildings_as_polygon_dict(
    buildings: Any,
    output_file: str = 'building_polygons.pkl',
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None
) -> Optional[Dict[int, List[Tuple[float, float]]]]:
    """
    Save building contours as a dictionary of polygons.
    Coordinates are converted to meters with (0,0) at the specified center point.

    Args:
        buildings: GeoDataFrame containing building footprints
        output_file: Path to save the polygon dictionary (default: 'building_polygons.pkl')
        center_lat: Latitude of center point for coordinate system (if None, uses first building centroid)
        center_lon: Longitude of center point for coordinate system (if None, uses first building centroid)

    Returns:
        Dictionary mapping building index to list of coordinate tuples [(x_meters, y_meters), ...],
        or None if conversion fails

    Example:
        >>> buildings = get_buildings_in_radius(52.37, 4.89, 400)
        >>> polygons = save_buildings_as_polygon_dict(buildings, center_lat=52.37, center_lon=4.89)
        >>> print(f"Saved {len(polygons)} building polygons")
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        return None

    try:
        import pickle

        # Define coordinate systems for conversion
        wgs84 = pyproj.CRS('EPSG:4326')
        utm31n = pyproj.CRS('EPSG:32631')  # UTM Zone 31N for Netherlands
        project_to_utm = pyproj.Transformer.from_crs(wgs84, utm31n, always_xy=True).transform

        # Determine center point
        if center_lat is None or center_lon is None:
            # Use centroid of first building
            first_geom = buildings.iloc[0].geometry
            center_lon = first_geom.centroid.x
            center_lat = first_geom.centroid.y
            print(f"Using automatic center: ({center_lat:.6f}, {center_lon:.6f})")
        else:
            print(f"Using specified center: ({center_lat:.6f}, {center_lon:.6f})")

        # Convert center to UTM
        center_x_utm, center_y_utm = project_to_utm(center_lon, center_lat)
        print(f"Center in UTM: ({center_x_utm:.2f}, {center_y_utm:.2f}) m")

        polygon_dict = {}

        print(f"Converting {len(buildings)} buildings to meters centered at (0,0)...", end='', flush=True)

        for idx, row in buildings.iterrows():
            geom = row.geometry

            # Handle both Polygon and MultiPolygon geometries
            if isinstance(geom, Polygon):
                # Extract exterior coordinates, convert to UTM, then center at origin
                coords = list(geom.exterior.coords)
                utm_coords = [project_to_utm(lon, lat) for lon, lat in coords]
                centered_coords = [(x - center_x_utm, y - center_y_utm) for x, y in utm_coords]
                polygon_dict[idx] = centered_coords
            elif isinstance(geom, MultiPolygon):
                # For MultiPolygon, store list of polygons
                multi_centered = []
                for poly in geom.geoms:
                    coords = list(poly.exterior.coords)
                    utm_coords = [project_to_utm(lon, lat) for lon, lat in coords]
                    centered_coords = [(x - center_x_utm, y - center_y_utm) for x, y in utm_coords]
                    multi_centered.append(centered_coords)
                polygon_dict[idx] = multi_centered

        # Save to pickle file
        with open(output_file, 'wb') as f:
            pickle.dump(polygon_dict, f)

        print(f" done")
        print(f"Saved {len(polygon_dict)} building contours to {output_file}")
        print(f"Coordinates are in meters with (0,0) at the center point")

        return polygon_dict

    except Exception as e:
        print(f"\nError saving polygon dictionary: {e}")
        return None


def plot_buildings_to_png(
    latitude: float,
    longitude: float,
    radius_meters: int = 1000,
    output_png: str = "buildings.png",
    dpi: int = 300,
    buildings: Optional[Any] = None
) -> bool:
    """
    Plot buildings that fall completely within a circle to a PNG file.
    Buildings are shown as solid black on white background.

    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_meters: Radius in meters around the coordinates (default: 1000m = 1km)
        output_png: Filename for the output PNG file (default: 'buildings.png')
        dpi: Resolution of the output image (default: 300)
        buildings: Optional pre-fetched GeoDataFrame of buildings. If None, will fetch buildings.

    Returns:
        True if successful, False otherwise

    Example:
        >>> plot_buildings_to_png(52.37, 4.89, radius_meters=500)
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        print("Install with: pip install osmnx geopandas folium matplotlib")
        return False

    try:
        # Fetch buildings only if not provided
        if buildings is None:
            buildings = get_buildings_in_radius(latitude, longitude, radius_meters)

        if buildings is None or len(buildings) == 0:
            return False

        print("Filtering buildings within circle...", end='', flush=True)

        # Create a circle in the same CRS as buildings (WGS84)
        # We need to project to a metric CRS to create accurate circle
        center_point = Point(longitude, latitude)

        # Project to UTM for accurate distance calculations
        # Determine UTM zone from longitude
        utm_zone = int((longitude + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone}" if latitude >= 0 else f"EPSG:{32700 + utm_zone}"

        # Create transformer
        project_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True).transform
        project_to_wgs84 = pyproj.Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True).transform

        # Transform center to UTM and create circle
        center_utm = transform(project_to_utm, center_point)
        circle_utm = center_utm.buffer(radius_meters)

        # Transform circle back to WGS84
        circle_wgs84 = transform(project_to_wgs84, circle_utm)

        # Filter buildings - keep only those completely within the circle
        buildings_within = buildings[buildings.geometry.within(circle_wgs84)]

        print(f" {len(buildings_within)}/{len(buildings)} buildings completely within circle")

        if len(buildings_within) == 0:
            print("No buildings completely within the circle")
            return False

        print("Creating plot...", end='', flush=True)

        # Project everything to UTM for accurate circular rendering
        buildings_within_utm = buildings_within.to_crs(utm_crs)
        circle_utm_gdf = gpd.GeoDataFrame([1], geometry=[circle_utm], crs=utm_crs)

        # Create figure with white background
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), facecolor='white')
        ax.set_facecolor('white')

        # Plot circle outline (optional, for reference)
        circle_utm_gdf.boundary.plot(ax=ax, color='lightgray', linewidth=1, linestyle='--')

        # Plot buildings in solid black
        buildings_within_utm.plot(ax=ax, color='black', edgecolor='black', linewidth=0.5)

        # Remove axis ticks and labels for clean look
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Set equal aspect ratio
        ax.set_aspect('equal')

        # Set axis limits to perfectly square bounds around circle in UTM (meters)
        bounds = circle_utm.bounds
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2

        # Circle is already in meters, so range should be equal in both dimensions
        max_range = radius_meters * 2 * 1.02  # 2% margin
        ax.set_ylim(center_y - max_range/2, center_y + max_range/2)

        # Tight layout
        plt.tight_layout(pad=0)

        # Save to PNG with fixed square dimensions
        plt.savefig(output_png, dpi=dpi, facecolor='white', bbox_inches=None)
        plt.close()

        print(f" done")
        print(f"Saved to {output_png} ({len(buildings_within)} buildings)")

        return True

    except Exception as e:
        print(f"\nError creating plot: {e}")
        return False


def visualize_buildings(
    latitude: float,
    longitude: float,
    radius_meters: int = 1000,
    output_html: str = 'buildings_map.html',
    buildings: Optional[Any] = None
) -> bool:
    """
    Visualize buildings on an interactive map and save as HTML.

    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_meters: Radius in meters around the coordinates (default: 1000m = 1km)
        output_html: Filename for the output HTML map (default: 'buildings_map.html')
        buildings: Optional pre-fetched GeoDataFrame of buildings. If None, will fetch buildings.

    Returns:
        True if successful, False otherwise

    Example:
        >>> visualize_buildings(52.37, 4.89, radius_meters=500)
        >>> # Opens buildings_map.html in your browser
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        print("Install with: pip install osmnx geopandas folium")
        return False

    try:
        # Fetch buildings only if not provided
        if buildings is None:
            buildings = get_buildings_in_radius(latitude, longitude, radius_meters)

        if buildings is None or len(buildings) == 0:
            return False

        # Create a folium map centered on the coordinates
        map_center = [latitude, longitude]
        m = folium.Map(location=map_center, zoom_start=15, tiles='OpenStreetMap')

        # Add a marker for the center point
        folium.Marker(
            location=map_center,
            popup=f'Center: ({latitude:.6f}, {longitude:.6f})',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

        # Add a circle showing the search radius
        folium.Circle(
            location=map_center,
            radius=radius_meters,
            color='blue',
            fill=True,
            fillOpacity=0.1,
            popup=f'{radius_meters}m radius'
        ).add_to(m)

        # Add buildings to the map
        # Convert to WGS84 (EPSG:4326) if needed
        if buildings.crs != 'EPSG:4326':
            buildings = buildings.to_crs('EPSG:4326')

        # Add each building as a polygon
        for idx, row in buildings.iterrows():
            # Create popup with building info
            building_type = row.get('building', 'unknown')
            popup_text = f"Building type: {building_type}"
            if 'name' in row and row['name']:
                popup_text += f"<br>Name: {row['name']}"

            # Convert geometry to GeoJSON and add to map
            folium.GeoJson(
                row.geometry,
                style_function=lambda x: {
                    'fillColor': 'orange',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                popup=folium.Popup(popup_text, max_width=200)
            ).add_to(m)

        # Save the map
        m.save(output_html)
        print(f"\nMap saved to {output_html}")
        print(f"Open the file in your browser to view the interactive map.")
        print(f"Total buildings displayed: {len(buildings)}")

        return True

    except Exception as e:
        print(f"Error creating visualization: {e}")
        return False


def plot_all_features_to_png(
    latitude: float,
    longitude: float,
    radius_meters: int = 1000,
    output_png: str = "features_map.png",
    dpi: int = 300,
    buildings: Optional[Any] = None
) -> bool:
    """
    Plot all geographic features (buildings, roads, waterways, etc.) within a circular area.
    Creates a comprehensive visualization showing the complete urban layout without text labels.

    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_meters: Radius in meters around the coordinates (default: 1000m = 1km)
        output_png: Filename for the output PNG file (default: 'features_map.png')
        dpi: Resolution of the output image (default: 300)
        buildings: Optional pre-fetched GeoDataFrame of buildings. If None, will fetch buildings.

    Returns:
        True if successful, False otherwise

    Example:
        >>> plot_all_features_to_png(52.37, 4.89, radius_meters=400, output_png="amsterdam_map.png")
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        print("Install with: pip install osmnx geopandas matplotlib")
        return False

    try:
        print(f"Fetching geographic features within {radius_meters}m...")

        # Use OSMnx to get the graph and geodataframes
        import osmnx as ox
        import time

        # Fetch buildings if not provided
        if buildings is None:
            print("Fetching buildings...", end='', flush=True)
            buildings = get_buildings_in_radius(latitude, longitude, radius_meters)
            if buildings is not None:
                print(f" {len(buildings)} found")
        else:
            print(f"Using provided buildings: {len(buildings)} found")

        # Fetch water features via Overpass API
        print("Fetching water features (canals, rivers)...", end='', flush=True)
        water = None
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json][timeout:30];
            (
              way["waterway"](around:{radius_meters},{latitude},{longitude});
              way["natural"="water"](around:{radius_meters},{latitude},{longitude});
              relation["waterway"](around:{radius_meters},{latitude},{longitude});
              relation["natural"="water"](around:{radius_meters},{latitude},{longitude});
            );
            out geom;
            """

            response = requests.post(overpass_url, data={'data': overpass_query}, timeout=60)
            response.raise_for_status()
            data = response.json()

            if 'elements' in data and len(data['elements']) > 0:
                water_list = []
                for element in data['elements']:
                    try:
                        poly = None
                        if element['type'] == 'way' and 'geometry' in element:
                            coords = [(node['lon'], node['lat']) for node in element['geometry']]
                            if len(coords) >= 2:
                                from shapely.geometry import LineString
                                # For waterways, create LineString or Polygon
                                tags = element.get('tags', {})
                                if coords[0] == coords[-1] and len(coords) >= 4:
                                    # Closed polygon (e.g., pond, lake)
                                    poly = Polygon(coords)
                                else:
                                    # Open linestring (e.g., canal, river)
                                    poly = LineString(coords).buffer(0.00005)  # Small buffer for visibility

                        if poly is not None and not poly.is_empty:
                            water_list.append({'geometry': poly})
                    except Exception:
                        continue

                if water_list:
                    water = gpd.GeoDataFrame(water_list, crs='EPSG:4326')
                    print(f" {len(water)} found")
                else:
                    print(" none found")
            else:
                print(" none found")
        except Exception as e:
            print(f" error: {e}")

        print("Fetching street network...", end='', flush=True)
        edges = None
        try:
            G = ox.graph_from_point((latitude, longitude), dist=radius_meters, network_type='all')
            # Convert graph to GeoDataFrames
            nodes, edges = ox.graph_to_gdfs(G)
            print(f" {len(edges)} edges found")
        except Exception as e:
            print(f" none found")

        # Create circle for clipping
        center_point = Point(longitude, latitude)
        utm_zone = int((longitude + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone}" if latitude >= 0 else f"EPSG:{32700 + utm_zone}"

        project_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True).transform
        project_to_wgs84 = pyproj.Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True).transform

        center_utm = transform(project_to_utm, center_point)
        circle_utm = center_utm.buffer(radius_meters)
        circle_wgs84 = transform(project_to_wgs84, circle_utm)

        print("\nCreating visualization...", end='', flush=True)

        # Project everything to UTM for accurate circular rendering
        circle_utm_gdf = gpd.GeoDataFrame([1], geometry=[circle_utm], crs=utm_crs)

        # Create figure with white background
        fig, ax = plt.subplots(1, 1, figsize=(12, 12), facecolor='white')
        ax.set_facecolor('white')

        # Plot circle boundary
        circle_utm_gdf.boundary.plot(ax=ax, color='black', linewidth=2)

        # Plot water features (canals, rivers, etc.) in blue
        if water is not None and len(water) > 0:
            water_within = water[water.geometry.intersects(circle_wgs84)]
            if len(water_within) > 0:
                water_within_utm = water_within.to_crs(utm_crs)
                water_within_utm.plot(ax=ax, color='#87CEEB', edgecolor='#4682B4', linewidth=0.5, alpha=0.7)
                print(f" {len(water_within)} water features plotted", end='')

        # Plot streets/roads in gray
        if edges is not None and len(edges) > 0:
            edges_within = edges[edges.geometry.intersects(circle_wgs84)]
            if len(edges_within) > 0:
                edges_within_utm = edges_within.to_crs(utm_crs)
                edges_within_utm.plot(ax=ax, color='#696969', linewidth=0.8, alpha=0.6)
                print(f", {len(edges_within)} road segments", end='')

        # Plot buildings in dark gray/black
        if buildings is not None and len(buildings) > 0:
            buildings_within = buildings[buildings.geometry.intersects(circle_wgs84)]
            if len(buildings_within) > 0:
                buildings_within_utm = buildings_within.to_crs(utm_crs)
                buildings_within_utm.plot(ax=ax, color='#2F4F4F', edgecolor='black', linewidth=0.3, alpha=0.8)
                print(f", {len(buildings_within)} buildings", end='')

        print("...")

        # Remove all axes, ticks, labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Set equal aspect ratio
        ax.set_aspect('equal')

        # Set axis limits to perfectly square bounds around circle in UTM (meters)
        bounds = circle_utm.bounds
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2

        # Circle is already in meters, so range should be equal in both dimensions
        max_range = radius_meters * 2 * 1.02  # 2% margin
        ax.set_xlim(center_x - max_range/2, center_x + max_range/2)
        ax.set_ylim(center_y - max_range/2, center_y + max_range/2)

        # Tight layout
        plt.tight_layout(pad=0)

        # Save to PNG with fixed square dimensions
        plt.savefig(output_png, dpi=dpi, facecolor='white', bbox_inches=None)
        plt.close()

        print(f"Saved visualization to {output_png}")
        return True

    except Exception as e:
        print(f"\nError creating visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


def plot_city_map_style(
    latitude: float,
    longitude: float,
    radius_circle_meters: int = 1000,
    radius_meters: int = 1000,
    output_png: str = "city_map.png",
    dpi: int = 300,
    buildings: Optional[Any] = None
) -> bool:
    """
    Create a traditional city plan/map style visualization with cartographic colors.
    Similar to buildings_map.html but as a PNG without any text labels.

    Args:
        latitude: Latitude of the center point
        longitude: Longitude of the center point
        radius_circle_meters: Radius of the plotted circle in meters (default: 1000m = 1km)
        radius_meters: Radius in meters around the coordinates (default: 1000m = 1km)
        output_png: Filename for the output PNG file (default: 'city_map.png')
        dpi: Resolution of the output image (default: 300)
        buildings: Optional pre-fetched GeoDataFrame of buildings. If None, will fetch buildings.

    Returns:
        True if successful, False otherwise

    Example:
        >>> plot_city_map_style(52.37, 4.89, radius_circle_meters=400, radius_meters=450, output_png="amsterdam_city_map.png")
    """
    if not BUILDING_VIZ_AVAILABLE:
        print("Error: Required libraries not installed.")
        print("Install with: pip install osmnx geopandas matplotlib")
        return False

    try:
        print(f"Creating city map style visualization within {radius_meters}m...")

        import osmnx as ox

        # Fetch buildings if not provided
        if buildings is None:
            print("Fetching buildings...", end='', flush=True)
            buildings = get_buildings_in_radius(latitude, longitude, radius_meters)
            if buildings is not None:
                print(f" {len(buildings)} found")
        else:
            print(f"Using provided buildings: {len(buildings)} found")

        # Fetch water features via Overpass API
        print("Fetching water features...", end='', flush=True)
        water = None
        try:
            import time
            overpass_url = "https://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json][timeout:30];
            (
              way["waterway"](around:{radius_meters},{latitude},{longitude});
              way["natural"="water"](around:{radius_meters},{latitude},{longitude});
              relation["waterway"](around:{radius_meters},{latitude},{longitude});
              relation["natural"="water"](around:{radius_meters},{latitude},{longitude});
            );
            out geom;
            """

            # Retry logic with exponential backoff
            max_retries = 3
            retry_delay = 2
            response = None

            for attempt in range(max_retries):
                try:
                    response = requests.post(overpass_url, data={'data': overpass_query}, timeout=60)
                    response.raise_for_status()
                    break
                except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f" retry {attempt + 1}/{max_retries} (waiting {wait_time}s)...", end='', flush=True)
                        time.sleep(wait_time)
                    else:
                        raise

            if response is None:
                raise Exception("Failed to fetch water data after retries")

            data = response.json()

            if 'elements' in data and len(data['elements']) > 0:
                water_list = []
                for element in data['elements']:
                    try:
                        poly = None
                        if element['type'] == 'way' and 'geometry' in element:
                            coords = [(node['lon'], node['lat']) for node in element['geometry']]
                            if len(coords) >= 2:
                                from shapely.geometry import LineString
                                if coords[0] == coords[-1] and len(coords) >= 4:
                                    poly = Polygon(coords)
                                else:
                                    poly = LineString(coords).buffer(0.00005)

                        if poly is not None and not poly.is_empty:
                            water_list.append({'geometry': poly})
                    except Exception:
                        continue

                if water_list:
                    water = gpd.GeoDataFrame(water_list, crs='EPSG:4326')
                    print(f" {len(water)} found")
                else:
                    print(" none found")
            else:
                print(" none found")
        except requests.exceptions.Timeout:
            print(f" timeout")
        except Exception as e:
            print(f" error: {str(e)}")

        # Fetch parks and green spaces via Overpass API
        print("Fetching parks and green spaces...", end='', flush=True)
        parks = None
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json][timeout:30];
            (
              way["leisure"="park"](around:{radius_meters},{latitude},{longitude});
              way["leisure"="garden"](around:{radius_meters},{latitude},{longitude});
              way["landuse"="grass"](around:{radius_meters},{latitude},{longitude});
              way["landuse"="meadow"](around:{radius_meters},{latitude},{longitude});
              way["landuse"="forest"](around:{radius_meters},{latitude},{longitude});
              way["natural"="wood"](around:{radius_meters},{latitude},{longitude});
              relation["leisure"="park"](around:{radius_meters},{latitude},{longitude});
              relation["leisure"="garden"](around:{radius_meters},{latitude},{longitude});
              relation["landuse"="grass"](around:{radius_meters},{latitude},{longitude});
            );
            out geom;
            """

            response = requests.post(overpass_url, data={'data': overpass_query}, timeout=60)
            response.raise_for_status()
            data = response.json()

            if 'elements' in data and len(data['elements']) > 0:
                parks_list = []
                for element in data['elements']:
                    try:
                        poly = None
                        if element['type'] == 'way' and 'geometry' in element:
                            coords = [(node['lon'], node['lat']) for node in element['geometry']]
                            if coords[0] != coords[-1] and len(coords) >= 3:
                                coords.append(coords[0])
                            if len(coords) >= 4:
                                poly = Polygon(coords)
                        elif element['type'] == 'relation' and 'members' in element:
                            # Handle relations (multi-part parks)
                            for member in element['members']:
                                if member.get('role') == 'outer' and 'geometry' in member:
                                    coords = [(node['lon'], node['lat']) for node in member['geometry']]
                                    if coords[0] != coords[-1] and len(coords) >= 3:
                                        coords.append(coords[0])
                                    if len(coords) >= 4:
                                        poly = Polygon(coords)
                                        break  # Use first outer polygon

                        if poly is not None and not poly.is_empty:
                            parks_list.append({'geometry': poly})
                    except Exception:
                        continue

                if parks_list:
                    parks = gpd.GeoDataFrame(parks_list, crs='EPSG:4326')
                    print(f" {len(parks)} found")
                else:
                    print(" none found")
            else:
                print(" none found")
        except requests.exceptions.Timeout:
            print(f" timeout")
        except Exception as e:
            print(f" error: {str(e)[:50]}")

        print("Fetching street network...", end='', flush=True)
        edges = None
        try:
            G = ox.graph_from_point((latitude, longitude), dist=radius_meters, network_type='all')
            nodes, edges = ox.graph_to_gdfs(G)
            print(f" {len(edges)} edges found")
        except Exception as e:
            print(f" none found")

        # Create circle for clipping
        center_point = Point(longitude, latitude)
        utm_zone = int((longitude + 180) / 6) + 1
        utm_crs = f"EPSG:{32600 + utm_zone}" if latitude >= 0 else f"EPSG:{32700 + utm_zone}"

        project_to_utm = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True).transform
        project_to_wgs84 = pyproj.Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True).transform

        center_utm = transform(project_to_utm, center_point)
        circle_utm = center_utm.buffer(radius_circle_meters)
        circle_wgs84 = transform(project_to_wgs84, circle_utm)

        print("\nCreating city map style visualization...", end='', flush=True)

        # Project everything to UTM for accurate circular rendering
        circle_utm_gdf = gpd.GeoDataFrame([1], geometry=[circle_utm], crs=utm_crs)

        # Create figure with light background (typical map background)
        fig, ax = plt.subplots(1, 1, figsize=(14, 14), facecolor='#E8E4DC')
        ax.set_facecolor('#E8E4DC')  # Light gray/beige ground color (different from white roads)

        # First, fill the entire circle with the background color
        circle_utm_gdf.plot(ax=ax, color='#E8E4DC', edgecolor='none', zorder=0)

        # Plot circle boundary (subtle)
        circle_utm_gdf.boundary.plot(ax=ax, color='#999999', linewidth=1.5, linestyle='-', zorder=10)

        # Plot water features first (bottom layer) - traditional blue
        if water is not None and len(water) > 0:
            water_within = water[water.geometry.intersects(circle_wgs84)]
            if len(water_within) > 0:
                water_within_utm = water_within.to_crs(utm_crs)
                water_within_utm.plot(ax=ax, color='#6BB6FF', edgecolor='#2E86DE', linewidth=0.8, alpha=1.0, zorder=1)
                print(f" {len(water_within)} water features", end='')

        # Plot parks and green spaces (layer 2) - green
        if parks is not None and len(parks) > 0:
            parks_within = parks[parks.geometry.intersects(circle_wgs84)]
            if len(parks_within) > 0:
                parks_within_utm = parks_within.to_crs(utm_crs)
                parks_within_utm.plot(ax=ax, color='#C8E6C9', edgecolor='#81C784', linewidth=0.5, alpha=0.85, zorder=2)
                print(f", {len(parks_within)} parks", end='')

        # Plot streets/roads with varied widths based on road type
        if edges is not None and len(edges) > 0:
            edges_within = edges[edges.geometry.intersects(circle_wgs84)].copy()
            if len(edges_within) > 0:
                edges_within_utm = edges_within.to_crs(utm_crs)
                # Classify roads by type for different styling
                for idx, row in edges_within_utm.iterrows():
                    # Get the original highway type from edges_within (before projection)
                    original_idx = edges_within.index.get_loc(idx) if idx in edges_within.index else None
                    if original_idx is not None:
                        highway_type = edges_within.iloc[original_idx].get('highway', 'unclassified')
                    else:
                        highway_type = 'unclassified'

                    # Determine line width based on road type
                    if highway_type in ['motorway', 'trunk', 'primary']:
                        linewidth = 4.0
                        color = '#FCD6A4'  # Light orange for major roads
                        edgecolor = '#C47E30'
                        zorder_base = 5
                    elif highway_type in ['secondary', 'tertiary']:
                        linewidth = 2.5
                        color = '#FFFFFF'  # White for secondary roads
                        edgecolor = '#999999'
                        zorder_base = 4
                    elif highway_type in ['residential', 'living_street', 'unclassified']:
                        linewidth = 1.5
                        color = '#FFFFFF'  # White
                        edgecolor = '#CCCCCC'
                        zorder_base = 3
                    else:  # paths, footways, etc
                        linewidth = 0.8
                        color = '#E8E8E8'
                        edgecolor = '#DDDDDD'
                        zorder_base = 3

                    # Plot road with casing (outline)
                    gpd.GeoSeries([row.geometry], crs=utm_crs).plot(
                        ax=ax, color=edgecolor, linewidth=linewidth + 1.0, zorder=zorder_base
                    )
                    # Plot road fill
                    gpd.GeoSeries([row.geometry], crs=utm_crs).plot(
                        ax=ax, color=color, linewidth=linewidth, zorder=zorder_base + 0.1
                    )

                print(f", {len(edges_within)} roads", end='')

        # Plot buildings (top layer) - warm building color like typical maps
        if buildings is not None and len(buildings) > 0:
            buildings_within = buildings[buildings.geometry.intersects(circle_wgs84)]
            if len(buildings_within) > 0:
                buildings_within_utm = buildings_within.to_crs(utm_crs)
                buildings_within_utm.plot(
                    ax=ax,
                    color='#E4D4C8',  # Light tan/beige for buildings
                    edgecolor='#8B7355',  # Darker brown outline
                    linewidth=0.5,
                    alpha=0.95,
                    zorder=8
                )
                print(f", {len(buildings_within)} buildings", end='')

        print(" done")

        # Remove all axes, ticks, labels for clean map appearance
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.axis('off')  # Turn off axis completely

        # Set equal aspect ratio
        ax.set_aspect('equal')

        # Set axis limits to perfectly square bounds around circle in UTM (meters)
        bounds = circle_utm.bounds
        center_x = (bounds[0] + bounds[2]) / 2
        center_y = (bounds[1] + bounds[3]) / 2

        # Circle is already in meters, so range should be equal in both dimensions
        max_range = radius_meters * 2 * 1.01  # 1% margin

        ax.set_xlim(center_x - max_range/2, center_x + max_range/2)
        ax.set_ylim(center_y - max_range/2, center_y + max_range/2)

        # Tight layout
        plt.tight_layout(pad=0)

        # Save to PNG with fixed square dimensions and matching background color
        plt.savefig(output_png, dpi=dpi, facecolor='#E8E4DC', bbox_inches=None)
        plt.close()

        print(f"Saved city map to {output_png}")
        return True

    except Exception as e:
        print(f"\nError creating city map: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Example usage of building visualization functions."""
    from weather import get_city_coordinates  # Import from weather module

    if not BUILDING_VIZ_AVAILABLE:
        print("Building visualization not available.")
        print("Install required packages: pip install osmnx geopandas folium matplotlib")
        return

    print("=" * 50)
    print("Building Visualization Demo")
    print("=" * 50)

    test_city = "Amsterdam, Netherlands"
    coords = get_city_coordinates(test_city)

    if coords:
        lat, lon = coords
        print(f"\nVisualizing buildings around {test_city}")

        # Fetch buildings once and save to GeoJSON
        buildings = get_buildings_in_radius(
            lat, lon,
            radius_meters=400,
            output_file="amsterdam_buildings.geojson"
        )

        # Reuse the fetched buildings for visualization and plotting
        if buildings is not None:
            # Save building contours as polygon dictionary (coordinates in meters, centered at Dam Square)
            print(f"\nSaving building contours as polygon dictionary...")
            polygon_dict = save_buildings_as_polygon_dict(
                buildings,
                "amsterdam_building_polygons.pkl",
                center_lat=lat,
                center_lon=lon
            )

            visualize_buildings(lat, lon, radius_meters=400, buildings=buildings)

            # Create PNG plot with buildings completely within circle
            #print(f"\nCreating PNG plot of buildings within circle...")
            #plot_buildings_to_png(lat, lon, radius_meters=400, output_png="buildings.png", buildings=buildings)

            # Create comprehensive visualization with all features
            #print(f"\nCreating comprehensive PNG with all features (roads, buildings, canals)...")
            #plot_all_features_to_png(lat, lon, radius_meters=400, output_png="amsterdam_complete_map.png", dpi=300, buildings=buildings)

            # Create city map style visualization (like a printed city plan)
            print(f"\nCreating city map style visualization...")
            plot_city_map_style(lat, lon, radius_circle_meters=400, radius_meters=450, output_png="amsterdam_city_plan.png", dpi=500, buildings=buildings)


if __name__ == "__main__":
    main()
