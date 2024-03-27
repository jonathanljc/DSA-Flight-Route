from data import DataFilter
from routes import FlightGraph
import time

class resultsObj(object):
    def __init__(self):
        
        self.dijkstra_time = None
        self.dijkstra_time_unit = None
        self.dijkstra_path = None
        self.dijkstra_total_distance = None 
        self.dijkstra_total_cost= None 
        self.dijkstra_total_cost_path= None
        self.dijkstra_all_paths = None
        self.dijkstra_all_explored_paths = None
        self.dijkstra_direct_flights = None
        self.dijkstra_connecting_flights = None
        self.dijkstra_valid_travel = None
  
        
        self.a_star_time = None
        self.a_star_time_unit = None
        self.a_star_path = None
        self.a_star_total_distance = None
        self.a_star_total_cost= None
        self.a_star_total_cost_path= None
        self.a_star_all_paths = None
        self.a_star_all_explored_paths = None
        self.a_star_direct_flights = None
        self.a_star_connecting_flights = None
        self.a_star_valid_travel = None

        
        self.bellman_ford_time = None
        self.bellman_ford_time_unit= None
        self.bellman_ford_path = None
        self.bellman_ford_total_distance = None
        self.bellman_ford_total_cost = None
        self.bellman_ford_all_total_cost_path= None
        self.bellman_ford_all_paths = None
        self.bellman_ford_all_explored_paths = None
        self.bellman_ford_direct_flights = None
        self.bellman_ford_connecting_flights = None
        self.bellman_ford_valid_travel = None

        self.dfs_time = None
        self.dfs_path = None
        self.dfs_total_distance = None
        self.dfs_total_cost = None
        self.dfs_total_cost_path = None
        self.dfs_all_paths = None
        self.dfs_all_explored_paths = None
        self.dfs_direct_flights = None
        self.dfs_connecting_flights = None
class FlightPlanner:
    def __init__(self, source, destination, *args, **kwargs):
        self.data_filter = DataFilter()
        self.airport_data = self.data_filter.airport_data
        self.route_data = self.data_filter.route_data
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
        results.dijkstra_all_paths= dijkstra_result[2]
        results.dijkstra_all_explored_paths = dijkstra_result[3]  # Store all explored paths from Dijkstra's
        results.dijkstra_total_cost_path=len(results.dijkstra_all_explored_paths)
        results.dijkstra_direct_flights, results.dijkstra_connecting_flights, results.dijkstra_valid_travel = self.flight_graph.findFlights(self.route_data, results.dijkstra_all_paths[0])
        results.dijkstra_direct_flights, results.dijkstra_connecting_flights = self.flight_graph.calculatePrice(results.dijkstra_direct_flights, results.dijkstra_connecting_flights, results.dijkstra_path, results.dijkstra_total_distance)
        
        start_time = time.time() #emperical reading start
        a_star_result = self.flight_graph.a_star(source, destination)
        end_time = time.time() #end
        results.a_star_time = end_time-start_time
        results.a_star_path = a_star_result[1] #store the path found by the algo
        results.a_star_total_distance = a_star_result[0]  # Store A* total cost
        results.a_star_total_cost=len(results.a_star_path) # Read the number of paths
        results.a_star_all_paths = a_star_result[2]  # Store all paths from A*
        results.a_star_all_explored_paths = a_star_result[3]  # Store all explored paths from A*
        results.a_star_total_cost_path=len(results.a_star_all_explored_paths)
        results.a_star_direct_flights, results.a_star_connecting_flights, results.a_star_valid_travel = self.flight_graph.findFlights(self.route_data, results.a_star_all_paths[0])
        results.a_star_direct_flights, results.a_star_connecting_flights = self.flight_graph.calculatePrice(results.a_star_direct_flights, results.a_star_connecting_flights, results.a_star_path, results.a_star_total_distance)
        
        # Bellman Ford
        start_time = time.time()  # empirical reading start
        bellman_ford_result = self.flight_graph.bellman_ford(source, destination)
        end_time = time.time()  # end
        results.bellman_ford_time = end_time - start_time
        results.bellman_ford_path = bellman_ford_result[1]  # store the path found by the algo
        results.bellman_ford_total_distance = bellman_ford_result[0]  # Store Bellman Ford's total cost
        results.bellman_ford_total_cost = len(results.bellman_ford_path)  # Read the number of paths
        results.bellman_ford_all_paths = bellman_ford_result[2]  # Store all paths from Bellman Ford
        results.bellman_ford_all_explored_paths = bellman_ford_result[3]  # Store all explored paths from Bellman Ford
        results.bellman_ford_all_total_cost_path=len(results.bellman_ford_all_explored_paths)
        results.bellman_ford_direct_flights, results.bellman_ford_connecting_flights, results.bellman_ford_valid_travel = self.flight_graph.findFlights(self.route_data, results.bellman_ford_all_paths[0])
        results.bellman_ford_direct_flights, results.bellman_ford_connecting_flights = self.flight_graph.calculatePrice(results.bellman_ford_direct_flights, results.bellman_ford_connecting_flights, results.bellman_ford_path, results.bellman_ford_total_distance)

        
        # Add this code to the find_flights method of the FlightPlanner class
        start_time = time.time()  # empirical reading start
        dfs_result = self.flight_graph.dfs(source, destination)
        end_time = time.time()  # end
        results.dfs_time = end_time - start_time
        results.dfs_path = dfs_result[1]  # store the path found by the algo
        results.dfs_total_distance = dfs_result[0]  # Store DFS total cost
        results.dfs_total_cost=len(results.dfs_path) # Read the number of paths
        results.dfs_all_paths = dfs_result[2]  # Store all paths from DFS
        results.dfs_all_explored_paths = dfs_result[3]  # Store all explored paths from DFS
        results.dfs_total_cost_path=len(results.dfs_all_explored_paths)
        #results.dfs_direct_flights, results.dfs_connecting_flights = self.flight_graph.findFlights(self.route_data, results.dfs_all_paths[0])
        #results.dfs_direct_flights, results.dfs_connecting_flights = self.flight_graph.calculatePrice(results.dfs_direct_flights, results.dfs_connecting_flights, results.dfs_path, results.dfs_total_distance)
        
        return results