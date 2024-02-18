# Import necessary functions from the data and routes modules
from data import filterData, calculateDistance
from routes import create_graph_kdtree, calculate_shortest_path

# Define the main function
def main():
    # Load and filter airport data using the filterData function from the data module
    airport_data = filterData()

    # Print the number of airports in Asia
    print(f"{len(airport_data)} airports in Asia")

    try:
        # Print the data for the airport with IATA code "SIN"
        print(airport_data["SIN"])

        # Calculate the distance between "SIN" and "PEK" using the calculateDistance function from the data module
        distance = calculateDistance(
            airport_data["SIN"]["latitude"], airport_data["SIN"]["longitude"],
            airport_data["PEK"]["latitude"], airport_data["PEK"]["longitude"]
        )
        # Print the calculated distance
        print(f"Distance from SIN to PEK: {distance} km")

        # (For Testing & maybe future use) Get user to enter IATA Code of airport to calculate
        inputAirport = input("Enter IATA Code: ")

        # Create a graph from the airport data using the create_graph_kdtree function from the routes module
        graph = create_graph_kdtree(airport_data)
        # Calculate the shortest paths from "SIN" using the calculate_shortest_path function from the routes module
        shortest_paths = calculate_shortest_path(graph, inputAirport)

        # Print the shortest paths
        print(shortest_paths)
    except KeyError as e:
        # Print an error message if a KeyError occurs (e.g., if "SIN" or "PEK" is not in the airport data)
        print(f"KeyError: {e}")

# If this script is run directly (not imported as a module), call the main function
if __name__ == "__main__":
    main()