import heapq
from data import DataFilter
from scipy.spatial import KDTree
import random

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

    def dfs(self, start, goal):
        stack = [(start, [start], 0)]  # Add a third element to the tuple for the total distance
        visited = set()
        all_paths = {start: [[start]]}  # Add a dictionary to keep track of all paths
        all_explored_paths = []  # List to store all explored paths

        while stack:
            (vertex, path, distance) = stack.pop()  # Update here
            if vertex not in visited:
                if vertex == goal:
                    costed_path = [(path[i], path[i+1], self.graph[path[i]][path[i+1]]) for i in range(len(path)-1)]
                    return distance, costed_path, all_paths[vertex], all_explored_paths  # Return the total distance, the costed path, all paths to the goal, and all explored paths
                visited.add(vertex)
                for neighbor in self.graph[vertex]:
                    stack.append((neighbor, path + [neighbor], distance + self.graph[vertex][neighbor]))  # Add the distance from vertex to neighbor to the total distance
                    all_paths[neighbor] = [path + [neighbor] for path in all_paths[vertex]]  # Update the paths for the neighbor
                    all_explored_paths.extend(all_paths[neighbor])  # Add all new paths to all_explored_paths

        return None  # If no path is found
    
    # Calculate the shortest path from a starting vertex to a target vertex using Dijkstra's algorithm
    def calculate_shortest_path(self, starting_vertex, target_vertex=None):
        shortest_distances = {vertex: float('infinity') for vertex in self.graph}
        shortest_distances[starting_vertex] = 0
        previous_vertices = {vertex: None for vertex in self.graph}
        heap = [(0, starting_vertex)]
        all_paths = {starting_vertex: [[starting_vertex]]}  # Add a dictionary to keep track of all paths
        all_explored_paths = []  # List to store all explored paths
        
        

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
                    all_paths[neighbor] = [path + [neighbor] for path in all_paths[current_vertex]]  # Update the paths for the neighbor
                    all_explored_paths.extend(all_paths[neighbor])  # Add all new paths to all_explored_paths

        path = []
        current_vertex = target_vertex
        while current_vertex is not None:
            path.append(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        path = path[::-1]
        costed_path = [(path[i], path[i+1], self.graph[path[i]][path[i+1]]) for i in range(len(path)-1)]
        return shortest_distances[target_vertex], costed_path, all_paths[target_vertex], all_explored_paths  # Return the total cost, the costed path, all paths to the target, and all explored paths

    # A* algorithm to find the shortest path from start to goal
    def a_star(self, start, goal):
        queue = []
        heapq.heappush(queue, (0, start))
        scores = {start: 0}
        came_from = {start: None}
        all_paths={start:[[start]]}
        all_explored_paths=[]

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
                    all_paths[neighbor] = [path + [neighbor] for path in all_paths[current]]
                    all_explored_paths.extend(all_paths[neighbor])  # Add all new paths to all_explored_paths


        path = self.reconstruct_path(came_from, start, goal)
        costed_path = [(path[i], path[i+1], self.graph[path[i]][path[i+1]]) for i in range(len(path)-1)]
        return scores[goal], costed_path, all_paths[goal], all_explored_paths  # Return the total cost and the costed path

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
    
    # Bellman Ford algorithm to find the shortest path from start to goal
    def bellman_ford(self, start, goal):
        distance = {vertex: float('infinity') for vertex in self.graph}
        distance[start] = 0
        predecessor = {vertex: None for vertex in self.graph}
        all_paths = {start: [[start]]}  # Add a dictionary to keep track of all paths
        all_explored_paths = []  # List to store all explored paths
        

        for _ in range(len(self.graph) - 1):
            for vertex in self.graph:
                for neighbor in self.graph[vertex]:
                    new_distance = distance[vertex] + self.graph[vertex][neighbor]
                    if new_distance < distance[neighbor]:
                        distance[neighbor] = new_distance
                        predecessor[neighbor] = vertex
                        all_paths[neighbor] = [path + [neighbor] for path in all_paths[vertex]]  # Update the paths for the neighbor
                        all_explored_paths.extend(all_paths[neighbor])  # Add all new paths to all_explored_paths

        for vertex in self.graph:
            for neighbor in self.graph[vertex]:
                assert distance[neighbor] <= distance[vertex] + self.graph[vertex][neighbor], "Graph contains a negative-weight cycle"

        path = []
        current_vertex = goal
        while current_vertex is not None:
            path.append(current_vertex)
            current_vertex = predecessor[current_vertex]
        path = path[::-1]
        costed_path = [(path[i], path[i+1], self.graph[path[i]][path[i+1]]) for i in range(len(path)-1)]
        return distance[goal], costed_path, all_paths[goal], all_explored_paths  # Return the total cost, the costed path, all paths to the goal, and all explored paths
        
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
                    #     # Calculate the cost of the flight
                    #     cost = self.graph[route["source"]][route["destination"]]
                    #     # Add the cost to the route dictionary
                    #     route_with_cost = {**route, 'cost': cost}

                    if route["destination"] == shortest_path[-1] and route["source"] == shortest_path[0]:
                        direct_flights.append(route)
                    else:
                        if route["destination"] != shortest_path[-1] and route["source"] == shortest_path[0]:
                            connecting_flights.append(route)
                        elif route["destination"] == shortest_path[-1] and route["source"] != shortest_path[0]:
                            connecting_flights.append(route)
                        elif route["destination"] != shortest_path[-1] and route["source"] != shortest_path[0] and route["destination"] != shortest_path[0]:
                            connecting_flights.append(route)

        for route in connecting_flights:
            if route['destination'] == shortest_path[-1]:
                validTravelFlag = 1
                break
            else:
                validTravelFlag = 0

        return direct_flights, connecting_flights, validTravelFlag
    
    def calculatePrice(self, direct_flights, connecting_flights, algo_path, total_dist):
        for flight in direct_flights:
            flight["price"] = round((total_dist * random.uniform(0.09, 0.11)), 2)
            flight["distance"] = round(total_dist, 2)
        
        for flight in connecting_flights:
            distTemp = 0.00000
            for path in algo_path:
                if flight["source"] == path[0]:
                    distTemp += path[2]
                if flight["destination"] == path[1]:
                    distTemp += path[2]
                    flight["price"] = round((distTemp * random.uniform(0.06, 0.09)), 2)
                    flight["distance"] = round(distTemp, 2)
            if flight["price"] == None:
                flight["price"] = "NA"
                flight["distance"] = "NA"
        
        return direct_flights, connecting_flights