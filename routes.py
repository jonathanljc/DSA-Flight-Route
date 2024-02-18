# Import the heapq module for creating min-heap, useful in graph algorithms like Dijkstra's.
import heapq
# Import the calculateDistance function that calculates the geographical distance between two points.
from data import calculateDistance
# Import KDTree, a space-partitioning data structure for organizing points in a k-dimensional space.
from scipy.spatial import KDTree

# Define a function to create a graph from the airport data using a k-d tree.
def create_graph_kdtree(airport_data, num_neighbors=100):
    # Initialize lists to store coordinates and IATA codes of airports.
    coordinates = []
    iata_codes = []
    # Loop through each airport in the data.
    for airport in airport_data.values():
        # Append the latitude and longitude of the airport to the coordinates list.
        coordinates.append((airport["latitude"], airport["longitude"]))
        # Append the IATA code of the airport to the iata_codes list.
        iata_codes.append(airport["iata"])

    # Create a KDTree with the coordinates of the airports.
    tree = KDTree(coordinates)

    # Initialize a dictionary to store the graph.
    graph = {}

    # Loop through each airport in the data.
    for i, airport in enumerate(airport_data.values()):
        # Query the KDTree for the nearest neighbors of the current airport.
        _, indices = tree.query(coordinates[i], k=num_neighbors+1)
        # Add the current airport and its nearest neighbors to the graph.
        graph[airport["iata"]] = {iata_codes[index]: calculateDistance(airport["latitude"], airport["longitude"], airport_data[iata_codes[index]]["latitude"], airport_data[iata_codes[index]]["longitude"]) for index in indices[1:]}

    # Return the created graph.
    return graph

# Define a function to calculate the shortest path from a starting vertex to all other vertices in the graph.
def calculate_shortest_path(graph, starting_vertex, target_vertex=None):
    # Initialize the shortest distances to all vertices as infinity.
    shortest_distances = {vertex: float('infinity') for vertex in graph}
    # The shortest distance to the starting vertex is 0.
    shortest_distances[starting_vertex] = 0
    # Initialize a set to keep track of visited vertices.
    visited = set()

    # Initialize the heap with the starting vertex.
    heap = [(0, starting_vertex)]
    # While there are vertices to be visited.
    while len(heap) > 0:
        # Pop the vertex with the smallest distance.
        current_distance, current_vertex = heapq.heappop(heap)

        # If the current vertex has already been visited, skip it.
        if current_vertex in visited:
            continue

        # Mark the current vertex as visited.
        visited.add(current_vertex)

        # If the current vertex is the target vertex, break from the loop.
        if current_vertex == target_vertex:
            break

        # For each neighbor of the current vertex.
        for neighbor, weight in graph[current_vertex].items():
            # Calculate the distance to the neighbor through the current vertex.
            distance = current_distance + weight

            # If the calculated distance is less than the currently known shortest distance to the neighbor.
            if distance < shortest_distances[neighbor]:
                # Update the shortest distance to the neighbor.
                shortest_distances[neighbor] = distance
                # Push the neighbor to the heap.
                heapq.heappush(heap, (distance, neighbor))

    # Return the shortest distances to all vertices.
    return shortest_distances