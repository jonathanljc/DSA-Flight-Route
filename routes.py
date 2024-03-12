# Import the heapq module for creating min-heap, useful in graph algorithms like Dijkstra's.
import heapq

# Import the calculateDistance function that calculates the geographical distance between two points.
from data import calculateDistance

# Import KDTree, a space-partitioning data structure for organizing points in a k-dimensional space.
# Install scipy if you don't have it installed.
# pip3 install scipy (mac), pip install scipy (windows)
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
    shortest_distances = {vertex: float('infinity') for vertex in graph}
    shortest_distances[starting_vertex] = 0
    previous_vertices = {vertex: None for vertex in graph}
    heap = [(0, starting_vertex)]

    while len(heap) > 0:
        current_distance, current_vertex = heapq.heappop(heap)

        if current_vertex == target_vertex:
            break

        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight

            if distance < shortest_distances[neighbor]:
                shortest_distances[neighbor] = distance
                previous_vertices[neighbor] = current_vertex
                heapq.heappush(heap, (distance, neighbor))

    path = []
    current_vertex = target_vertex
    while current_vertex is not None:
        path.append(current_vertex)
        current_vertex = previous_vertices[current_vertex]
    path = path[::-1]

    return shortest_distances, path

# def findDirectFlight(path, route_data, airline_data):
#     directFlightsID = []
#     directFlightsName = []
#     sourceAirport = path[0]
#     destinationAirport = path[-1]

#     # Check if there is a direct flight
#     for route in route_data:
#         if route["source"] == sourceAirport:
#             if route["destination"] == destinationAirport:
#                 directFlightsID.append(route["airlineID"])
    
#     if len(directFlightsID) == 0:
#         return f"No direct flights from {path[0]} to {path[-1]}"
#     else:
#         for x in directFlightsID:
#             for airline in airline_data:
#                 if x == airline["airlineID"]:
#                     directFlightsName.append(airline["airlineName"])
            
#     return f"Direct Flights from {path[0]} to {path[-1]}: {', '.join(directFlightsName)}"

def findFlights(route_data, shortest_path):
    airportsList = shortest_path[:-1]  # Exclude source and destination airports
    connecting_flights = []
    direct_flights = []

    for airport in airportsList:
        # Check if there are routes departing from the connecting airport
        departing_routes = [route for route in route_data if route["source"] == airport]

        for route in departing_routes:
            # Check if the destination of the route is one of the airports in the shortest path
            if route["destination"] in shortest_path:
                # if route source is airport source and destination route is airport destination = direct flight
                if route["destination"] == shortest_path[-1] and route["source"] == shortest_path[0]:
                    direct_flights.append(route)
                else:
                    # if route destination is not airport destination BUT route source is airport source = connecting flight
                    if route["destination"] != airportsList[-1] and route["source"] == shortest_path[0]:
                        connecting_flights.append(route)

                    # if route source is not airport source BUT route destination IS airport destination = connecting flight
                    if route["destination"] == airportsList[-1] and route["source"] != shortest_path[0]:
                        connecting_flights.append(route)

                    # if route source/destination is not airport source AND not airport destination
                    # AND route destination is not airport source = connecting flight
                    if route["destination"] != airportsList[-1] and route["source"] != shortest_path[0] and route["destination"] != airportsList[0]:
                        connecting_flights.append(route)

    if len(direct_flights) == 0:
        print("No direct flights found.")
    else:
        print("Direct Flights:")
        for flight in direct_flights:
            print(flight)

    
    if len(connecting_flights) == 0:
        print("No connecting flights found.")
    else:
        print("Connecting Flights:")
        for flight in connecting_flights:
        # connecting_flight_info.append(f"Flight {flight['airlineID']} from {flight['source']} to {flight['destination']}")
            print(flight)
