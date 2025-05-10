import os
from functools import lru_cache
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import networkx as nx
import osmnx as ox
from shapely.geometry import LineString
import pyproj

router = APIRouter(prefix="/water-route", tags=["water-routing"])

# -----------------------------
# Pydantic models
# -----------------------------
class RouteResponse(BaseModel):
    coordinates: list[tuple[float, float]]  # List of (lon, lat)
    distance: float                         # in meters
    duration: float | None = None          # optional
    ascent: float | None = None            # optional
    descent: float | None = None           # optional

# -----------------------------
# Projection transformers
# -----------------------------
_proj_to_merc = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
_proj_to_wgs = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

# -----------------------------
# Helper: densify path
# -----------------------------
def densify_path(coords: list[tuple[float, float]], max_dist: float = 5.0) -> tuple[list[tuple[float, float]], float]:
    if not coords:
        return [], 0.0
    merc_pts = [_proj_to_merc.transform(lon, lat) for lon, lat in coords]
    line = LineString(merc_pts)
    total_length = line.length
    if total_length <= 0:
        return coords, 0.0
    intervals = list(range(0, int(total_length), int(max_dist)))
    if intervals[-1] != total_length:
        intervals.append(total_length)
    densified: list[tuple[float, float]] = []
    for dist in intervals:
        pt = line.interpolate(dist)
        if pt.is_empty:
            continue
        lon, lat = _proj_to_wgs.transform(pt.x, pt.y)
        densified.append((lon, lat))
    return densified, total_length

# -----------------------------
# Load and cache water graph
# -----------------------------
@lru_cache(maxsize=1)
def load_water_graph() -> nx.MultiDiGraph:
    graph_file = os.getenv("WATER_GRAPH_FILE", "data/bashkortostan_water.graphml")
    if os.path.exists(graph_file):
        return ox.load_graphml(graph_file)
    # Download graph from Overpass without simplification
    gdf = ox.geocode_to_gdf("Republic of Bashkortostan, Russia")
    if gdf.empty:
        raise RuntimeError("Cannot fetch boundaries for Bashkortostan")
    polygon = gdf.iloc[0].geometry
    custom_filter = '["waterway"~"river"]'
    G = ox.graph_from_polygon(
        polygon,
        network_type="all",
        custom_filter=custom_filter,
        simplify=False  # preserve all vertices
    )
    # Do NOT simplify the graph: retain detailed geometry
    # G = ox.simplify_graph(G)
    os.makedirs(os.path.dirname(graph_file), exist_ok=True)
    ox.save_graphml(G, graph_file)
    return G

# -----------------------------
# Compute route
# -----------------------------
def compute_water_route(
    G: nx.MultiDiGraph,
    origin: tuple[float, float],  # (lat, lon)
    destination: tuple[float, float]
) -> tuple[list[tuple[float, float]], float]:
    # Find nearest graph nodes
    orig_node = ox.distance.nearest_nodes(G, X=origin[1], Y=origin[0])
    dest_node = ox.distance.nearest_nodes(G, X=destination[1], Y=destination[0])

    # Compute shortest path by node IDs
    try:
        route_nodes = nx.shortest_path(G, source=orig_node, target=dest_node, weight="length")
    except nx.NetworkXNoPath:
        route_nodes = []

    # If no path, fallback straight line
    if len(route_nodes) < 2:
        start = (origin[1], origin[0])
        end = (destination[1], destination[0])
        x1, y1 = _proj_to_merc.transform(start[0], start[1])
        x2, y2 = _proj_to_merc.transform(end[0], end[1])
        length = ((x2-x1)**2 + (y2-y1)**2)**0.5
        return [start, end], length

    # Collect node coordinates (lon,lat) in order
    node_coords = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in route_nodes]
    # Compute total length by summing edge lengths
    length = 0.0
    for u, v in zip(route_nodes[:-1], route_nodes[1:]):
        data = next(iter(G.get_edge_data(u, v).values()))
        length += data.get('length', 0)

    # Densify along straight line through nodes
    # project to mercator
    merc_pts = [_proj_to_merc.transform(lon, lat) for lon, lat in node_coords]
    line = LineString(merc_pts)
    # densify at 5m intervals
    intervals = list(range(0, int(line.length), 5))
    intervals.append(int(line.length))
    densified: list[tuple[float, float]] = []
    for d in intervals:
        pt = line.interpolate(d)
        if pt.is_empty:
            continue
        lon, lat = _proj_to_wgs.transform(pt.x, pt.y)
        densified.append((lon, lat))

    # Override endpoints exactly
    start = (origin[1], origin[0])
    end = (destination[1], destination[0])
    densified[0] = start
    densified[-1] = end

    return densified, length

# -----------------------------
# API endpoint
# -----------------------------
@router.get("", response_model=RouteResponse)
def route_water(
    origin_lat: float = Query(..., alias="origin.lat"),
    origin_lon: float = Query(..., alias="origin.lon"),
    destination_lat: float = Query(..., alias="destination.lat"),
    destination_lon: float = Query(..., alias="destination.lon")
):
    G = load_water_graph()
    path, length = compute_water_route(
        G,
        origin=(origin_lat, origin_lon),
        destination=(destination_lat, destination_lon)
    )
    return RouteResponse(coordinates=path, distance=length)
