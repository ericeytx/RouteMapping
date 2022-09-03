from math import sin, cos, sqrt, atan2, radians
import random

import pandas as pd
import geopandas as gpd
import itertools
from geopy import distance
from geopy.geocoders import Nominatim
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
ox.config(use_cache=True, log_console=True)


def create_graph(loc, dist, transport_mode, loc_type="address"):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    if loc_type == "address":
        G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    elif loc_type == "points":
        G = ox.graph_from_point(loc, dist=dist, network_type=transport_mode )
    return G


def polygon_centroid(vertexes):
    _x_list = [vertex [0] for vertex in vertexes]
    _y_list = [vertex [1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return(_x, _y)


locator = Nominatim(user_agent="myGeocoder")

home_address = "6303 West Shady Shores Road, Denton, TX 76208"
home_location = [locator.geocode(home_address)]

appt_addresses = ["502 Oakland St, Denton, TX 76201",
    "3228 Teasley Ln, Denton, TX 76208",
    "3020 N Locust St, Denton, TX 76209"]

appt_locations = [locator.geocode(x) for x in appt_addresses]

coordinates = [(l.latitude, l.longitude) for l in appt_locations]

# x = [c[0] for c in coordinates]
# y = [c[1] for c in coordinates]
# centroid_coordinates = (sum(x) / len(coordinates), sum(y) / len(coordinates))

# centroid_coordinates = polygon_centroid(coordinates)

centroid_coordinates = ((min([c[0] for c in coordinates]) + max([c[0] for c in coordinates])) / 2,
                        (min([c[1] for c in coordinates]) + max([c[1] for c in coordinates])) / 2)

max_straight_line_distance = max([distance.distance(c, centroid_coordinates).m for c in coordinates])

G = create_graph(centroid_coordinates, max_straight_line_distance * 1.05, "drive_service", "points")

G = ox.add_edge_speeds(G) #Impute
G = ox.add_edge_travel_times(G) #Travel time

routes = []

for permutation in list(itertools.permutations(appt_locations)):
    stops = home_location + list(permutation) + home_location
    permutation_route = []
    travel_time = 0.0
    for x in range(0, len(stops) - 1):
        start_node = ox.get_nearest_node(G, coordinates[x])
        end_node = ox.get_nearest_node(G, coordinates[x+1]) #Calculate the shortest path
        travel_time += nx.shortest_path (G, start_node, end_node, weight='travel_time')
        permutation_route.append(nx.shortest_path(G, start_node, end_node, weight='travel_time'))
        if not routes:
            routes = permutation_route
        elif (sum(permutation_route) < sum(routes)):
            routes = permutation_route

# for x in range(0, len(addresses) - 1):
#     start_node = ox.get_nearest_node(G, coordinates[x])
#     end_node = ox.get_nearest_node(G, coordinates[x+1]) #Calculate the shortest path
#     #routes.append(nx.shortest_path(G, start_node, end_node, weight='travel_time'))
#     routes.append(nx.shortest_path(G, start_node, end_node, weight='travel_time'))

color = [ "red", "blue", "green", "yellow", "purple", "orange" ]
colors = [random.choice(color) for i in range(0, len(routes))]

print(colors)

ox.plot_graph_routes(G, routes, colors, route_linewidth=4, node_size=0)
