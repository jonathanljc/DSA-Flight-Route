# Import necessary functions from the data and routes modules
from data import filterData, calculateDistance, filterRouteData
from routes import create_graph_kdtree, calculate_shortest_path

# Define the main function
def main():
    # Load and filter airport data using the filterData function from the data module
    airport_data = filterData()

    # Load and filter routes using the filterRouteData function from the data module
    route_data = filterRouteData(airport_data)

    # Print the number of airports and routes in Asia
    print(f"{len(airport_data)} airports in Asia")
    print(f"{len(route_data)} routes in Asia")

    try:
        # Get user to enter IATA Code of starting airport
        inputAirport = input("Enter starting IATA Code: ")

        # Get user to enter IATA Code of target airport
        targetAirport = input("Enter target IATA Code: ")

        # Print the data for the starting and target airports
        print(airport_data[inputAirport])
        print(airport_data[targetAirport])

        # Calculate the distance between inputAirport and targetAirport using the calculateDistance function from the data module
        distance = calculateDistance(
            airport_data[inputAirport]["latitude"], airport_data[inputAirport]["longitude"],
            airport_data[targetAirport]["latitude"], airport_data[targetAirport]["longitude"]
        )
        # Print the calculated distance
        print(f"Distance from {inputAirport} to {targetAirport}: {distance} km")
        

        # Create a graph from the airport data using the create_graph_kdtree function from the routes module
        graph = create_graph_kdtree(airport_data)

        # Calculate the shortest path from inputAirport to targetAirport using the calculate_shortest_path function from the routes module
        shortest_paths = calculate_shortest_path(graph, inputAirport, targetAirport)

        shortest_distances, shortest_path = calculate_shortest_path(graph, inputAirport, targetAirport)
        print(f"Shortest path from {inputAirport} to {targetAirport}: {' -> '.join(shortest_path)}")
    except KeyError as e:
        # Print an error message if a KeyError occurs (e.g., if inputAirport or targetAirport is not in the airport data)
        print(f"KeyError: {e}")

# If this script is run directly (not imported as a module), call the main function
if __name__ == "__main__":
    main()