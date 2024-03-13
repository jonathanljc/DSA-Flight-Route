# Import necessary modules
from data import DataFilter
from routes import FlightGraph
from flightPlanner import FlightPlanner
from guiTest import App
        
# Main function
if __name__ == "__main__":
    # Get the source and destination from the user
    source = input("Enter starting IATA Code: ")
    destination = input("Enter target IATA Code: ")
    # Create a flight planner
    planner = FlightPlanner(source, destination)
    # Create a graph
    planner.create_graph()
    # Find flights from the source to the destination
    planner.find_flights(source, destination)

    app = App(source, destination)
    app.start()