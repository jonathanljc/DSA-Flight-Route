from data import DataFilter
from routes import FlightGraph
import time

class resultsObj(object):
    def __init__(self):
        self.dijkstra_time = None
        self.dijkstra_time_unit = None
        self.dijkstra_path = None
        self.dijkstra_path_easy = []
        self.dijkstra_direct_flights = None
        self.dijkstra_connecting_flights = None
        self.dijkstra_total_distance = None 
        self.dijkstra_total_cost= None 
        self.a_star_time = None
        self.a_star_time_unit = None
        self.a_star_path = None
        self.a_star_path_easy = []
        self.a_star_direct_flights = None
        self.a_star_connecting_flights = None
        self.a_star_total_distance = None
        self.a_star_total_cost= None 
        

class FlightPlanner:
    def __init__(self, source, destination, *args, **kwargs):
        self.data_filter = DataFilter()
        self.airport_data = self.data_filter.airport_data
        self.route_data = self.data_filter.route_data
        self.airline_data = self.data_filter.airline_data
        self.flight_graph = FlightGraph(self.airport_data)

    def create_graph(self):
        self.graph = self.flight_graph.graph

    def find_flights(self, source, destination):
        results = resultsObj()
        
        start_time = time.time() #emperical reading start
        dijkstra_result = self.flight_graph.calculate_shortest_path(source, destination)  
        end_time = time.time() #end
        results.dijkstra_time = end_time-start_time
        results.dijkstra_path = dijkstra_result[1] #store the path found by the algo
        results.dijkstra_total_distance = dijkstra_result[0]  # Store Dijkstra's total cost
        results.dijkstra_total_cost=len(results.dijkstra_path)# Read the number of paths

        for x in range(len(dijkstra_result[1])):
            results.dijkstra_path_easy.append(dijkstra_result[1][x][0])
            if x == (len(dijkstra_result[1])-1):
                results.dijkstra_path_easy.append(dijkstra_result[1][x][1])
        results.dijkstra_direct_flights, results.dijkstra_connecting_flights = self.flight_graph.findFlights(self.route_data, results.dijkstra_path_easy)
        
        
        start_time = time.time() #emperical reading start
        a_star_result = self.flight_graph.a_star(source, destination)
        end_time = time.time() #end
        results.a_star_time = end_time-start_time
        results.a_star_path = a_star_result[1] #store the path found by the algo
        results.a_star_total_distance = a_star_result[0]  # Store A* total cost
        results.a_star_total_cost=len(results.a_star_path) # Read the number of paths

        for x in range(len(a_star_result[1])):
            results.a_star_path_easy.append(a_star_result[1][x][0])
            if x == (len(a_star_result[1])-1):
                results.a_star_path_easy.append(a_star_result[1][x][1])
        results.a_star_direct_flights, results.a_star_connecting_flights = self.flight_graph.findFlights(self.route_data, results.a_star_path_easy)
        

        return results