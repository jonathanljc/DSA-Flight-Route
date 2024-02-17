# Import necessary modules and functions
import heapq
from data import calculateDistance

# Function to create a graph from the airport data
def create_graph(airport_data, num_neighbors=5):
    # Initialize an empty graph
    graph = {}
    # Iterate over all airports in the data
    for airport1 in airport_data.values():
        # Initialize an empty list to store distances
        distances = []
        # Calculate the distance from the current airport to all other airports
        for airport2 in airport_data.values():
            # Avoid calculating the distance from the airport to itself
            if airport1["iata"] != airport2["iata"]:
                # Calculate the distance between the two airports
                distance = calculateDistance(airport1["latitude"], airport1["longitude"], airport2["latitude"], airport2["longitude"])
                # Add the distance and the IATA code of the second airport to the list
                distances.append((distance, airport2["iata"]))
        # Sort the distances in ascending order
        distances.sort()
        # Add the current airport and its nearest neighbors to the graph
        graph[airport1["iata"]] = {iata: distance for distance, iata in distances[:num_neighbors]}
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