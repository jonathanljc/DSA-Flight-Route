# Import necessary modules and functions
import heapq
from data import calculateDistance
from scipy.spatial import KDTree

# Function to create a graph from the airport data using a k-d tree
def create_graph_kdtree(airport_data, num_neighbors=100):
    # Create a list of coordinates and a corresponding list of IATA codes
    coordinates = []
    iata_codes = []
    for airport in airport_data.values():
        coordinates.append((airport["latitude"], airport["longitude"]))
        iata_codes.append(airport["iata"])

    # Build a k-d tree
    tree = KDTree(coordinates)

    # Initialize an empty graph
    graph = {}

    # Iterate over all airports in the data
    for i, airport in enumerate(airport_data.values()):
        # Query the k-d tree for the nearest neighbors of the current airport
        _, indices = tree.query(coordinates[i], k=num_neighbors+1)  # +1 because the airport itself is included

        # Add the current airport and its nearest neighbors to the graph
        graph[airport["iata"]] = {iata_codes[index]: calculateDistance(airport["latitude"], airport["longitude"], airport_data[iata_codes[index]]["latitude"], airport_data[iata_codes[index]]["longitude"]) for index in indices[1:]}  # Skip the first neighbor because it's the airport itself

    # Return the graph
    return graph

# Function to calculate the shortest path from a starting vertex to all other vertices in the graph
def calculate_shortest_path(graph, starting_vertex, target_vertex=None):
    shortest_distances = {vertex: float('infinity') for vertex in graph}
    shortest_distances[starting_vertex] = 0
    visited = set()

    heap = [(0, starting_vertex)]
    while len(heap) > 0:
        current_distance, current_vertex = heapq.heappop(heap)

        if current_vertex in visited:
            continue

        visited.add(current_vertex)

        if current_vertex == target_vertex:
            break

        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight

            if distance < shortest_distances[neighbor]:
                shortest_distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))

    return shortest_distances
