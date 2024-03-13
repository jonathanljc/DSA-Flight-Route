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
        # Calculate the shortest path from inputAirport to targetAirport using the calculate_shortest_path function from the routes module
        shortest_paths = calculate_shortest_path(graph, inputAirport, targetAirport)

        shortest_distances, shortest_path = calculate_shortest_path(graph, inputAirport, targetAirport)
        print(f"Shortest path from {inputAirport} to {targetAirport}: {' -> '.join(shortest_path)}")

        # Find flights from source to destination
        findFlights(route_data, shortest_path)

    except KeyError as e:
        # Print an error message if a KeyError occurs (e.g., if inputAirport or targetAirport is not in the airport data)
        print(f"KeyError: {e}")

    return inputAirport, targetAirport

# If this script is run directly (not imported as a module), call the main function
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
    inputAirport, targetAirport = main()
    #app = App(inputAirport, targetAirport)
    #app.start()
    try:
        app = App(inputAirport, targetAirport)
        app.start()
    except AttributeError as e:
        if "_PhotoImage__photo" in str(e):
            pass  # Ignore this specific AttributeError
        else:
            raise  # Re-raise any other AttributeError
