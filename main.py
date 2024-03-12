from data import DataFilter
from routes import FlightGraph
import time

class FlightPlanner:
    def __init__(self):
        self.data_filter = DataFilter()
        self.airport_data = self.data_filter.airport_data
        self.route_data = self.data_filter.route_data
        self.airline_data = self.data_filter.airline_data
        self.flight_graph = FlightGraph(self.airport_data)

    def create_graph(self):
        self.graph = self.flight_graph.graph

    def find_flights(self, source, destination):
        start_time = time.time()
        shortest_path_dijkstra = self.flight_graph.calculate_shortest_path(source, destination)[1]
        end_time = time.time()
        print(f"Execution time of Dijkstra's algorithm: {end_time - start_time} seconds")

        print(f"Shortest path from {source} to {destination} using Dijkstra's algorithm: {' -> '.join(shortest_path_dijkstra)}")
    
        # Call findFlights method from FlightGraph class
        flights_dijkstra = self.flight_graph.findFlights(self.route_data, shortest_path_dijkstra)
        print(flights_dijkstra)

        start_time = time.time()
        shortest_path_a_star = self.flight_graph.a_star(source, destination)[1]
        end_time = time.time()
        print(f"Execution time of A* algorithm: {end_time - start_time} seconds")

        print(f"Shortest path from {source} to {destination} using A* algorithm: {' -> '.join(shortest_path_a_star)}")
    
        # Call findFlights method from FlightGraph class
        flights_a_star = self.flight_graph.findFlights(self.route_data, shortest_path_a_star)
        print(flights_a_star)
        
if __name__ == "__main__":
    planner = FlightPlanner()
    planner.create_graph()
    source = input("Enter starting IATA Code: ")
    destination = input("Enter target IATA Code: ")
    planner.find_flights(source, destination)