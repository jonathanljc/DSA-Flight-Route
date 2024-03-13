import heapq
from data import DataFilter
from scipy.spatial import KDTree

# Class to represent a flight graph
class FlightGraph:
    # Initialize the flight graph with airport data and number of neighbors
    def __init__(self, airport_data, num_neighbors=100):
        self.data_filter = DataFilter()
        self.airport_data = airport_data
        self.num_neighbors = num_neighbors
        self.graph = self.create_graph_kdtree()

    # Create a graph using KDTree for efficient nearest neighbor search
    def create_graph_kdtree(self):
        coordinates = []
        iata_codes = []
        # Loop through all airports and collect their coordinates and IATA codes
        for airport in self.airport_data.values():
            coordinates.append((airport["latitude"], airport["longitude"]))
            iata_codes.append(airport["iata"])
        # Create a KDTree with the coordinates
        tree = KDTree(coordinates)
        graph = {}
        # For each airport, find its nearest neighbors and add them to the graph
        for i, airport in enumerate(self.airport_data.values()):
            _, indices = tree.query(coordinates[i], k=self.num_neighbors+1)
            graph[airport["iata"]] = {iata_codes[index]: self.data_filter.calculate_distance(airport["latitude"], airport["longitude"], self.airport_data[iata_codes[index]]["latitude"], self.airport_data[iata_codes[index]]["longitude"]) for index in indices[1:]}
        return graph

    # Calculate the shortest path from a starting vertex to a target vertex using Dijkstra's algorithm
    def calculate_shortest_path(self, starting_vertex, target_vertex=None):
        shortest_distances = {vertex: float('infinity') for vertex in self.graph}
        shortest_distances[starting_vertex] = 0
        previous_vertices = {vertex: None for vertex in self.graph}
        heap = [(0, starting_vertex)]

        while len(heap) > 0:
            current_distance, current_vertex = heapq.heappop(heap)

            if current_vertex == target_vertex:
                break

            for neighbor, weight in self.graph[current_vertex].items():
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

    # Reconstruct the path from start to goal
    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()  # Reverse the path to get it from start to goal
        return path

    # Heuristic function for A* algorithm
    def heuristic(self, a, b):
        return abs(b[0] - a[0]) + abs(b[1] - a[1])

    # A* algorithm to find the shortest path from start to goal
    def a_star(self, start, goal):
        queue = []
        heapq.heappush(queue, (0, start))
        scores = {start: 0}
        came_from = {start: None}

        while queue:
            _, current = heapq.heappop(queue)

            if current == goal:
                break

            for neighbor in self.graph[current]:
                tentative_score = scores[current] + self.graph[current][neighbor]
                if neighbor not in scores or tentative_score < scores[neighbor]:
                    scores[neighbor] = tentative_score
                    priority = tentative_score + self.heuristic((self.airport_data[goal]["latitude"], self.airport_data[goal]["longitude"]), (self.airport_data[neighbor]["latitude"], self.airport_data[neighbor]["longitude"]))
                    heapq.heappush(queue, (priority, neighbor))
                    came_from[neighbor] = current

        return scores, self.reconstruct_path(came_from, start, goal)

    # Find flights for a given route data and shortest path
    def findFlights(self, route_data, shortest_path):
        airportsList = shortest_path[:-1]  # Exclude destination airport
        connecting_flights = []
        direct_flights = []

        # Loop through all airports in the shortest path
        for airport in airportsList:
            departing_routes = [route for route in route_data if route["source"] == airport]

            # Loop through all departing routes from the current airport
            for route in departing_routes:
                if route["destination"] in shortest_path:
                    if route["destination"] == shortest_path[-1] and route["source"] == shortest_path[0]:
                        direct_flights.append(route)
                    else:
                        if route["destination"] != shortest_path[-1] and route["source"] == shortest_path[0]:
                            connecting_flights.append(route)
                        elif route["destination"] == shortest_path[-1] and route["source"] != shortest_path[0]:
                            connecting_flights.append(route)
                        elif route["destination"] != shortest_path[-1] and route["source"] != shortest_path[0] and route["destination"] != shortest_path[0]:
                            connecting_flights.append(route)

        # Print direct and connecting flights
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
                print(flight)