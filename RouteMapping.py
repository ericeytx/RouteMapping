from math import sin, cos, sqrt, atan2, radians

import pandas as pd
import geopandas as gpd
from geopy import distance
from geopy.geocoders import Nominatim
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
ox.config(use_cache=True) #, log_console=True)


def create_graph(loc, dist, transport_mode, loc_type="address"):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    if loc_type == "address":
        G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    elif loc_type == "points":
        G = ox.graph_from_point(loc, dist=dist, network_type=transport_mode )
    return G


locator = Nominatim(user_agent="myGeocoder")

start_address = "502 Oakland St, Denton, TX 76201"
end_address = "3228 Teasley Ln, Denton, TX 76208"

start_location = locator.geocode(start_address)
end_location = locator.geocode(end_address)

start_coordinates = (start_location.latitude, start_location.longitude)
end_coordinates = (end_location.latitude, end_location.longitude)

center_coordinates = [sum(y) / len(y) for y in zip(*(start_coordinates, end_coordinates))]

straight_line_distance = distance.distance(start_coordinates, end_coordinates).m

G = create_graph(center_coordinates, straight_line_distance * 0.6, "drive_service", "points")
# ox.plot_graph(G)

G = ox.add_edge_speeds(G) #Impute
G = ox.add_edge_travel_times(G) #Travel time

start_node = ox.get_nearest_node(G, start_coordinates)
end_node = ox.get_nearest_node(G, end_coordinates) #Calculate the shortest path
route = nx.shortest_path(G, start_node, end_node, weight='travel_time') #Plot the route and street networks
ox.plot_graph_route(G, route, route_linewidth=4, node_size=0) #, bgcolor='k',fig_width=12, fig_height=12 )
