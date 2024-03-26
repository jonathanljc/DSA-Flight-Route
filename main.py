import customtkinter
import time
import math
from tkintermapview import TkinterMapView
from data import DataFilter
from routes import FlightGraph
from flightPlanner import FlightPlanner
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from tkinter import ttk # For tabs

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):

    APP_NAME = "Flight Map Routing System"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        self.additional_window = None
        self.planner = None
        self.results = None
        self.start_coordinate = None
        self.destination_coordinate = None
        self.airport_data = DataFilter.filter_airport_data(self)
        self.status_variable = customtkinter.Variable()  # Variable to hold the status

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(11, weight=1)
        
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=0, column=0, padx=(20, 20), pady=(10, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=2, column=0, padx=(20, 20), pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))
        
        self.label_start = customtkinter.CTkLabel(self.frame_left, text="Start (IATA Code):", anchor="w")
        self.label_start.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))

        self.entry_start = customtkinter.CTkEntry(self.frame_left, placeholder_text="Enter start IATA")
        self.entry_start.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.label_destination = customtkinter.CTkLabel(self.frame_left, text="Destination (IATA Code):", anchor="w")
        self.label_destination.grid(row=6, column=0, padx=(20, 20), pady=(10, 0))

        self.entry_destination = customtkinter.CTkEntry(self.frame_left, placeholder_text="Enter destination IATA")
        self.entry_destination.grid(row=7, column=0, padx=(20, 20), pady=(10, 0))

        self.search_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Search",
                                                command=self.search_event)
        self.search_button.grid(row=8, column=0, padx=(20, 20), pady=(30, 0))
        
        self.status_label = customtkinter.CTkLabel(self.frame_left, 
                                                   text="Status:")
        self.status_label.grid(row=9, column=0, padx=(20, 20), pady=(45, 0))
        
        self.status_code = customtkinter.CTkLabel(self.frame_left, textvariable=self.status_variable, wraplength=140, justify="center")
        self.status_code.grid(row=10, column=0, padx=(10, 10), pady=(1, 0))


        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(0, weight=95)
        self.frame_right.grid_rowconfigure(1, weight=5)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.additional_button = customtkinter.CTkButton(master=self.frame_right,
                                                 text="Search Results",
                                                 command=self.open_additional_window)
        self.additional_button.grid(row=1, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew", columnspan=3)


        # Set default values
        self.map_widget.set_address("Singapore")
        self.map_option_menu.set("Google normal")
        self.appearance_mode_optionemenu.set("System")
        self.status_code.configure(text_color="green")
        self.status_variable.set("Ready!")


    # additional window for displaying all search information
    def open_additional_window(self):
        
        if self.status_variable.get() != "Search Completed!":
            self.status_code.configure(text_color="red")
            self.status_variable.set("Please search for flights first!")
            return
        
        print("Additional Information")
        self.additional_window = customtkinter.CTkToplevel(self)
        self.additional_window.title("Additional Information")
        self.additional_window.geometry("600x600")
        self.additional_window.minsize(600, 600)
        
        # Set the additional window to be always on top
        self.additional_window.attributes("-topmost", True)

        style = ttk.Style()

        # Check the theme used by tkinter
        print(style.theme_use())

        # Set a theme that supports changing the tab colors
        style.theme_use('default')

        # Configure the Tab style
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='black', foreground='white')
        style.map('TNotebook.Tab', background=[('selected', 'black')], foreground=[('selected', 'white')])

        # Create notebook
        notebook = ttk.Notebook(self.additional_window, style='TNotebook')
        notebook.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Configure the grid to expand with the window
        self.additional_window.grid_rowconfigure(0, weight=1)
        self.additional_window.grid_columnconfigure(0, weight=1)

        # Create frames for each tab
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)

        # Add the frames to the notebook
        notebook.add(tab1, text='Dijkstra Algorithm')
        notebook.add(tab2, text='A* Algorithm')
        notebook.add(tab3, text='Bellman-Ford Algorithm')

        
        # Create a scrollable frame with a black background
        scrollable_frame = customtkinter.CTkScrollableFrame(tab1, bg_color="black", label_text="Search Results")
        scrollable_frame.pack(fill="both", expand=True)

        # Second scrollable frame
        scrollable_frame2 = customtkinter.CTkScrollableFrame(tab2, bg_color="black", label_text="Search Results")
        scrollable_frame2.pack(fill="both", expand=True)

        # Third scrollable frame
        scrollable_frame3 = customtkinter.CTkScrollableFrame(tab3, bg_color="black", label_text="Search Results")
        scrollable_frame3.pack(fill="both", expand=True)
        
        # Create labels to display information
        dijkstra_path_label = customtkinter.CTkLabel(scrollable_frame, text=f"Dijkstra Path: {' -> '.join(self.results.dijkstra_all_paths[0])}")
        dijkstra_path_label.pack()

        # Display the Dijkstra algorithm path
        for index, segment in enumerate(self.results.dijkstra_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame, text=f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)")
            path_label.pack()

        # Display total distance for Dijkstra's algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame, text=f"Total Distance: {self.results.dijkstra_total_distance:.2f} km")
        total_distance_label.pack()

        # Create labels to display information for A* algorithm
        a_star_path_label = customtkinter.CTkLabel(scrollable_frame2, text=f"A* Path: {' -> '.join(self.results.a_star_all_paths[0])}")
        a_star_path_label.pack()

        # Display the A* algorithm path
        for index, segment in enumerate(self.results.a_star_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame2, text=f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)")
            path_label.pack()

        # Display total distance for A* algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame2, text=f"Total Distance (A*): {self.results.a_star_total_distance:.2f} km")
        total_distance_label.pack()


        # Create labels to display information for Bellman-Ford algorithm
        bellman_ford_path_label = customtkinter.CTkLabel(scrollable_frame3, text=f"Bellman Ford Path: {' -> '.join(self.results.bellman_ford_all_paths[0])}")
        bellman_ford_path_label.pack()

        # Display the Bellman Ford algorithm path
        for index, segment in enumerate(self.results.bellman_ford_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame3, text=f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)")
            path_label.pack()

        # Display total distance for Bellman Ford algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame3, text=f"Total Distance (Bellman Ford): {self.results.bellman_ford_total_distance:.2f} km")
        total_distance_label.pack()

        if self.results.dijkstra_connecting_flights[-1] != "valid":
            dijkstra_connecting_warning_label = customtkinter.CTkLabel(scrollable_frame, text="WARNING: UNABLE TO REACH DESTINATION BASED ON PATH")
            dijkstra_connecting_warning_label.pack()
        
        # Display the cheapest path for Dijkstra's algorithm
        cheapest_path_label = customtkinter.CTkLabel(scrollable_frame, text=f"Cheapest Path: ")
        cheapest_path_label.pack()
        
        # Create a dictionary to store the cheapest flight for each unique combination of source and destination
        cheapest_flights = {}
        print(self.results.dijkstra_connecting_flights)
        # Iterate through each flight in self.results.dijkstra_connecting_flights
        for flight in self.results.dijkstra_connecting_flights:
            source = flight['source']
            destination = flight['destination']
            price = flight['price']
            
            # Check if this combination of source and destination already exists in the dictionary
            if (source, destination) not in cheapest_flights:
                # If it doesn't exist, add it to the dictionary with the current flight as the cheapest option
                cheapest_flights[(source, destination)] = flight
            else:
                # If it does exist, compare the price of the current flight with the cheapest price stored in the dictionary
                current_cheapest_price = cheapest_flights[(source, destination)]['price']
                if price < current_cheapest_price:
                    # If the current flight is cheaper, update the dictionary with this flight as the new cheapest option
                    cheapest_flights[(source, destination)] = flight

        # Display the cheapest flights
        for flight in cheapest_flights.values():
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text=f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}", 
                command=None,
                )
            flight_button.pack(pady=5)
                
        # Display dijkstra direct and connecting flights
        dijkstra_direct_flights_label = customtkinter.CTkLabel(scrollable_frame, text="Direct Flights:")
        dijkstra_direct_flights_label.pack()
        if len(self.results.dijkstra_direct_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text="No direct flights available", 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.dijkstra_direct_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame, 
                    text=f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}", 
                    command=None,
                    )
                flight_button.pack(pady=5)
            
        dijkstra_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame, text="Connecting Flights:")
        dijkstra_connecting_flights_label.pack()

        for flight in self.results.dijkstra_connecting_flights:
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text=f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}", 
                command=None,
                )
            flight_button.pack(pady=5)
            
        
        # Add a button to close the additional window
        close_button = customtkinter.CTkButton(self.additional_window, text="Close", command=self.additional_window.destroy)
        close_button.pack()
        
    # set start marker
    def set_start_marker(self, start_iata):
        try: 
            # Use geopy to get the coordinates of the start location based on the IATA code
            geolocator = Nominatim(user_agent="flightRouteMeasurements")
            searchQuery = start_iata + " Airport"
            start_location = geolocator.geocode(searchQuery)

            if start_location:
                # Extract latitude and longitude
                start_lat, start_lon = start_location.latitude, start_location.longitude
                # Set marker on the map widget
                startMarker = self.map_widget.set_marker(start_lat, start_lon)
                startMarker.set_text(start_iata)
                
                
                if start_iata not in self.airport_data:
                    self.show_error_message(f"Start location ({start_iata}) is not a valid airport in Asia.")
                    self.start_coordinate = None
                    self.map_widget.set_position(start_lat, start_lon)
                    self.map_widget.set_zoom(3)
                    self.update()
                    return 
                
                self.start_coordinate = (start_lat, start_lon)
        
        except GeocoderTimedOut:
            self.show_error_message("Geocoding service timed out while fetching start location.")

    # set destination marker
    def set_destination_marker(self, destination_iata):
        try:
            # Use geopy to get the coordinates of the destination location based on the IATA code
            geolocator = Nominatim(user_agent="flightRouteMeasurements")
            searchQuery = destination_iata + " Airport"
            destination_location = geolocator.geocode(searchQuery)

            if destination_location:
                # Extract latitude and longitude
                dest_lat, dest_lon = destination_location.latitude, destination_location.longitude
                # Set marker on the map widget
                destMarker = self.map_widget.set_marker(dest_lat, dest_lon)
                destMarker.set_text(destination_iata)
                
                if not self.start_coordinate:
                    return
                
                # Check if the location is in Asia
                if destination_iata not in self.airport_data:
                    self.show_error_message(f"Destination location ({destination_iata}) is not a valid airport in Asia.")
                    self.destination_coordinate = None
                    self.map_widget.set_position(dest_lat, dest_lon)
                    self.map_widget.set_zoom(3)
                    self.update()
                    return
                
                self.destination_coordinate = (dest_lat, dest_lon)
                
        except GeocoderTimedOut:
            self.show_error_message("Geocoding service timed out while fetching destination location.")
   
   # calculate zoom level
    def calculate_zoom_level(self, min_lat, max_lat, min_lon, max_lon):
        # Calculate the distance between the markers
        lat_distance = max_lat - min_lat
        lon_distance = max_lon - min_lon

        # Adjust the distance to include a padding (10% in this case)
        lat_padding = lat_distance * 0.1
        lon_padding = lon_distance * 0.1

        # Calculate the zoom level based on the distance
        lat_zoom = self.calculate_zoom(lat_distance + 2 * lat_padding)
        lon_zoom = self.calculate_zoom(lon_distance + 2 * lon_padding)

        # Use the smaller of the two zoom levels
        return min(lat_zoom, lon_zoom)

    # calculate zoom
    def calculate_zoom(self, distance):
        # Calculate the zoom level based on the distance
        # This is a simplified calculation, you may need to adjust it based on your map widget's specifications
        return round(14 - math.log2(distance / 360))

    # Search route from start to destination
    def search_event(self, event=None):
        try:
            # Retrieve input values
            start_iata = self.entry_start.get()
            destination_iata = self.entry_destination.get()

            if not start_iata or not destination_iata:
                self.status_code.configure(text_color="red")
                self.status_variable.set("Please enter both start and destination IATA codes!")
                return
            
            self.status_code.configure(text_color="red")
            self.status_variable.set("Checking IATA codes and Setting markers ...")
            self.update()

            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.set_start_marker(start_iata)
            self.set_destination_marker(destination_iata)
            self.update()
            
            if not self.start_coordinate or not self.destination_coordinate:
                # Update status to indicate searching
                self.status_code.configure(text_color="red")
                self.status_variable.set("Airports outside of Asia are not supported.")
                self.update()
                return
            
            # Determine the bounding box that encompasses both markers
            min_lat = min(self.start_coordinate[0], self.destination_coordinate[0])
            max_lat = max(self.start_coordinate[0], self.destination_coordinate[0])
            min_lon = min(self.start_coordinate[1], self.destination_coordinate[1])
            max_lon = max(self.start_coordinate[1], self.destination_coordinate[1])

            # Calculate the center of the bounding box
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2

            # Calculate the zoom level based on the bounding box dimensions
            # zoom_level = self.calculate_zoom_level(min_lat, max_lat, min_lon, max_lon)

            # Set the center and zoom level of the map widget
            self.map_widget.set_position(center_lat, center_lon)
            self.map_widget.set_zoom(3)
            self.update()
            
            # Update status to indicate searching
            self.status_code.configure(text_color="red")
            self.status_variable.set("Searching Routes, Please Wait...")
            self.update()
            
            # Perform search operation
            print("Search")

            self.planner = FlightPlanner(start_iata, destination_iata)
            self.planner.create_graph()
            self.results = self.planner.find_flights(start_iata, destination_iata)

            # For checking the "results" returned from line above
            print(f"Dijkstra's algorithm time(empirical): {self.results.dijkstra_time} 'seconds'")
            print(f"Dijkstra's algorithm path: {self.results.dijkstra_path}")
            print(f"Dijkstra's algorithm total distance: {self.results.dijkstra_total_distance}")
            print(f"Dijkstra's algorithm total cost: {self.results.dijkstra_total_cost}")
            # print(f"Dijkstra's algorithm direct flights: {self.results.dijkstra_direct_flights}")
            # print(f"Dijkstra's algorithm connecting flights: {self.results.dijkstra_connecting_flights}")
            print(f"Dijkstra's algorithm all paths: {self.results.dijkstra_all_paths}")
            print(f"Dijkstra's algorithm all explored paths: {self.results.dijkstra_total_cost_path}")  # Print all explored paths
            
            print(f"A* algorithm time(empirical): {self.results.a_star_time} 'seconds'")
            print(f"A* algorithm path: {self.results.a_star_path}")
            print(f"A* algorithm total distance: {self.results.a_star_total_distance}")
            print(f"A* algorithm total cost: {self.results.a_star_total_cost}")
            # print(f"A* algorithm direct flights: {self.results.a_star_direct_flights}")
            # print(f"A* algorithm connecting flights: {self.results.a_star_connecting_flights}")
            print(f"A* algorithm all paths: {self.results.a_star_all_paths}")
            print(f"A* algorithm all explored paths: {self.results.a_star_total_cost_path}")  # Print all explored paths
            
            # print the results of the Bellman-Ford algorithm
            print(f"Bellman-Ford algorithm time(empirical): {self.results.bellman_ford_time} 'seconds'")
            print(f"Bellman-Ford algorithm path: {self.results.bellman_ford_path}")
            print(f"Bellman-Ford algorithm total distance: {self.results.bellman_ford_total_distance}")
            print(f"Bellman-Ford algorithm total cost: {self.results.bellman_ford_total_cost}")
            # print(f"Bellman-Ford algorithm direct flights: {self.results.bellman_ford_direct_flights}")
            # print(f"Bellman-Ford algorithm connecting flights: {self.results.bellman_ford_connecting_flights}")
            print(f"Bellman-Ford algorithm all paths: {self.results.bellman_ford_all_paths}")
            print(f"Bellman-Ford algorithm all explored paths: {self.results.bellman_ford_all_total_cost_path}")
            
            # print the results of the DFS algorithm
        #    print(f"DFS algorithm time(empirical): {self.results.dfs_time} 'seconds'")
        #    print(f"DFS algorithm path: {self.results.dfs_path}")
        #    print(f"DFS algorithm total distance: {self.results.dfs_total_distance}")
        #    print(f"DFS algorithm total cost: {self.results.dfs_total_cost}")
            # print(f"DFS algorithm direct flights: {self.results.dfs_direct_flights}")
            # print(f"DFS algorithm connecting flights: {self.results.dfs_connecting_flights}")
        #    print(f"DFS algorithm all paths: {self.results.dfs_all_paths}")
          #  print(f"DFS algorithm all explored paths: {self.results.dfs_all_explored_paths}")
        #    print(f"DFS algorithm total cost path: {self.results.dfs_total_cost_path}")
           
            
          
            
            # Do something with the input values
            print("Start IATA:", start_iata)
            print("Destination IATA:", destination_iata)
            
            # Set markers and paths for the Dijkstra path
            
            path_markers = self.setMarkersAndPaths(self.results.dijkstra_path)

            self.status_code.configure(text_color="green")
            self.status_variable.set("Search Completed!")
            self.update()
            
        except Exception as e:
            # Handle the error
            print("An error occurred:", e)
            self.status_code.configure(text_color="red")
            self.status_variable.set("An error occurred during the search.")
            self.show_error_message(str(e))

    def setMarkersAndPaths(self, path):
        # Store all markers created for the path
        path_markers = []

        # Display the Dijkstra algorithm path and set markers
        for index, segment in enumerate(path):
            location1, location2, distance = segment
            
            searchLoc1 = location1 + " Airport"
            searchLoc2 = location2 + " Airport"

            # Use geopy to get the coordinates of the location based on the IATA code
            geolocator = Nominatim(user_agent="flightRouteMeasurements")
            
            try:
                location1_coordinates = geolocator.geocode(searchLoc1)
                location2_coordinates = geolocator.geocode(searchLoc2)
            except GeocoderTimedOut:
                self.show_error_message(f"Geocoding service timed out while fetching coordinates for {location1} or {location2}.")
                return
            
            if location1_coordinates and location2_coordinates:
                try:
                    # Extract latitude and longitude
                    location1_lat, location1_lon = location1_coordinates.latitude, location1_coordinates.longitude
                    location2_lat, location2_lon = location2_coordinates.latitude, location2_coordinates.longitude

                    # Set markers on the map widget
                    marker1 = self.map_widget.set_marker(location1_lat, location1_lon)
                    marker1.set_text(location1)
                    path_markers.append(marker1)

                    marker2 = self.map_widget.set_marker(location2_lat, location2_lon)
                    marker2.set_text(location2)
                    path_markers.append(marker2)

                    # Create a path between the markers
                    path = self.map_widget.set_path([(location1_lat, location1_lon), (location2_lat, location2_lon)], color="red")
                    path_markers.append(path)
                except Exception as e:
                    self.show_error_message(f"An error occurred while setting markers or path: {str(e)}")
                    return

        # Return the list of markers and paths
        return path_markers
    
    def show_error_message(self, message):
        # Create a new top-level window for the error message
        error_window = customtkinter.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x200")
        
        error_window.attributes("-topmost", True)

        # Create a scrollable frame inside the error window
        scrollable_frame = customtkinter.CTkScrollableFrame(error_window)
        scrollable_frame.pack(fill="both", expand=True)

        # Create a label to display the error message inside the scrollable frame
        error_label = customtkinter.CTkLabel(scrollable_frame, text=message, font=("Helvetica", 12), text_color="red", wraplength=280, justify="center")
        error_label.pack(pady=20)
                
    # need to be changed
    def set_map_focus_event(self):
        print("Set Map Focus")
        
    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        if self.additional_window:
            self.additional_window.destroy()  # Close the additional window if it exists

        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()