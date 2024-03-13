# Import necessary functions from the data and routes modules
from data import filterAirportData, calculateDistance, filterRouteData, filterAirline, filterAirportDataFurther
from routes import create_graph_kdtree, calculate_shortest_path, findFlights
from guiTest import App

# Define the main function
def main():
    # Load and filter airport data using the filterData function from the data module
    # airport_data is a dictionary containing the IATA code of each airport as the key and the airport data as the value
    airport_data = filterAirportData()

    # Load and filter routes using the filterRouteData function from the data module
    # route data is a list of dictionaries containing the source, destination and airline ID of each route
    route_data = filterRouteData(airport_data)

    # Futher filters the airports to only those airports that have a commercial flight route
    # (Remove this if dont want to implement this filter)
    commercial_airport_data = filterAirportDataFurther(airport_data, route_data)

    # Using only commercial airport data
    airport_data = commercial_airport_data

    # Load airlines using the filterRouteData function from the data module
    # airline_data is a dictionary containing the IATA code of each airline as the key and the airline data as the value
    airline_data = filterAirline()


    # Print the number of airports and routes in Asia
    print(f"{len(airport_data)} commercial airports in Asia")
    print(f"{len(route_data)} routes in Asia")

    try:
        # Get user to enter IATA Code of starting airport
        inputAirport = input("Enter starting IATA Code: ")

        # Get user to enter IATA Code of target airport
        targetAirport = input("Enter target IATA Code: ")

        # Print the data for the starting and target airports
        # print(airport_data[inputAirport])
        # print(airport_data[targetAirport])

        # Calculate the distance between inputAirport and targetAirport using the calculateDistance function from the data module
        distance = calculateDistance(
            airport_data[inputAirport]["latitude"], airport_data[inputAirport]["longitude"],
            airport_data[targetAirport]["latitude"], airport_data[targetAirport]["longitude"]
        )
        # Print the calculated distance
        print(f"Distance from {inputAirport} to {targetAirport}: {distance} km")
        
        print("Calculating shortest path...")


        # Create a graph from the airport data using the create_graph_kdtree function from the routes module
        graph = create_graph_kdtree(airport_data)

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
