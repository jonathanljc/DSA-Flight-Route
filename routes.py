# Import necessary modules and functions
import heapq
from data import calculateDistance
from scipy.spatial import KDTree

# Function to create a graph from the airport data using a k-d tree
def create_graph_kdtree(airport_data, num_neighbors=5):
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
        distances, indices = tree.query(coordinates[i], k=num_neighbors+1)  # +1 because the airport itself is included

        # Add the current airport and its nearest neighbors to the graph
        graph[airport["iata"]] = {iata_codes[index]: distance for distance, index in zip(distances[1:], indices[1:])}  # Skip the first neighbor because it's the airport itself

    # Return the graph
    return graph

# Function to calculate the shortest path from a starting vertex to all other vertices in the graph
def calculate_shortest_path(graph, starting_vertex):
    # Initialize the shortest distances to all vertices as infinity
    shortest_distances = {vertex: float('infinity') for vertex in graph}
    # The distance from the starting vertex to itself is 0
    shortest_distances[starting_vertex] = 0
    # Initialize an empty set to store the visited vertices
    visited = set()

    # Initialize a heap with the starting vertex
    heap = [(0, starting_vertex)]
    # Continue until all vertices have been visited
    while len(heap) > 0:
        # Pop the vertex with the shortest distance from the heap
        current_distance, current_vertex = heapq.heappop(heap)

        # If the current vertex has already been visited, skip it
        if current_vertex in visited:
            continue

        # Add the current vertex to the set of visited vertices
        visited.add(current_vertex)

        # Update the shortest distances to the neighbors of the current vertex
        for neighbor, weight in graph[current_vertex].items():
            # Calculate the distance to the neighbor through the current vertex
            distance = current_distance + weight

            # If this distance is shorter than the previously known shortest distance to the neighbor, update it
            if distance < shortest_distances[neighbor]:
                shortest_distances[neighbor] = distance
                # Add the neighbor to the heap
                heapq.heappush(heap, (distance, neighbor))

    # Return the shortest distances to all vertices
    return shortest_distances