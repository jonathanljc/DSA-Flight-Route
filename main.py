# Import necessary modules
from data import DataFilter
from routes import FlightGraph
import time

# Class to represent a flight planner
class FlightPlanner:
    # Initialize the flight planner with data filter, airport data, route data, airline data, and flight graph
    def __init__(self):
        self.data_filter = DataFilter()
        self.airport_data = self.data_filter.airport_data
        self.route_data = self.data_filter.route_data
        self.airline_data = self.data_filter.airline_data
        self.flight_graph = FlightGraph(self.airport_data)

    # Create a graph using the flight graph
    def create_graph(self):
        self.graph = self.flight_graph.graph

    # Find flights from a source to a destination
    def find_flights(self, source, destination):
        # Calculate the shortest path using Dijkstra's algorithm and measure the execution time
        start_time = time.time()
        shortest_path_dijkstra = self.flight_graph.calculate_shortest_path(source, destination)[1]
        end_time = time.time()
        print(f"Execution time of Dijkstra's algorithm: {end_time - start_time} seconds")

        # Print the shortest path
        print(f"Shortest path from {source} to {destination} using Dijkstra's algorithm: {' -> '.join(shortest_path_dijkstra)}")
    
        # Find flights for the shortest path
        flights_dijkstra = self.flight_graph.findFlights(self.route_data, shortest_path_dijkstra)
        print(flights_dijkstra)

        # Calculate the shortest path using A* algorithm and measure the execution time
        start_time = time.time()
        shortest_path_a_star = self.flight_graph.a_star(source, destination)[1]
        end_time = time.time()
        print(f"Execution time of A* algorithm: {end_time - start_time} seconds")

        # Print the shortest path
        print(f"Shortest path from {source} to {destination} using A* algorithm: {' -> '.join(shortest_path_a_star)}")
    
        # Find flights for the shortest path
        flights_a_star = self.flight_graph.findFlights(self.route_data, shortest_path_a_star)
        print(flights_a_star)
        
# Main function
if __name__ == "__main__":
    # Create a flight planner
    planner = FlightPlanner()
    # Create a graph
    planner.create_graph()
    # Get the source and destination from the user
    source = input("Enter starting IATA Code: ")
    destination = input("Enter target IATA Code: ")
    # Find flights from the source to the destination
    planner.find_flights(source, destination)