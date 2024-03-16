import customtkinter
import time
import math
from tkintermapview import TkinterMapView
from data import DataFilter
from routes import FlightGraph
from flightPlanner import FlightPlanner
from geopy.geocoders import Nominatim

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):

    APP_NAME = "TkinterMapView with CustomTkinter"
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
        self.status_label.grid(row=9, column=0, padx=(20, 20), pady=(50, 0))
        
        self.status_code = customtkinter.CTkLabel(self.frame_left, textvariable=self.status_variable)
        self.status_code.grid(row=10, column=0, padx=(20, 20), pady=(1, 0))


        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(0, weight=95)
        self.frame_right.grid_rowconfigure(1, weight=5)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.additional_button = customtkinter.CTkButton(master=self.frame_right,
                                                 text="Additional Information",
                                                 command=self.open_additional_window)
        self.additional_button.grid(row=1, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew", columnspan=3)


        # Set default values
        self.map_widget.set_address("Singapore")
        self.map_option_menu.set("Google normal")
        self.appearance_mode_optionemenu.set("System")
        self.status_code.configure(text_color="green")
        self.status_variable.set("Ready!")


    # need to be changed
    def open_additional_window(self):
        
        if self.status_variable.get() != "Done!":
            self.status_code.configure(text_color="red")
            self.status_variable.set("Please search for flights first!")
            return
        
        print("Additional Information")
        self.additional_window = customtkinter.CTkToplevel(self)
        self.additional_window.title("Additional Information")
        self.additional_window.geometry("600x600")
        self.additional_window.minsize(600, 600)
        
        # Create a scrollable frame with a black background
        scrollable_frame = customtkinter.CTkScrollableFrame(self.additional_window, bg_color="black", label_text="Search Results")
        scrollable_frame.pack(fill="both", expand=True)
        
        # Create labels for each result        
        dijkstra_path_label = customtkinter.CTkLabel(scrollable_frame, text=f"Dijkstra Path: {' -> '.join(self.results.dijkstra_path_easy)}")
        dijkstra_path_label.pack()

        dijkstra_direct_flights_label = customtkinter.CTkLabel(scrollable_frame, text="Dijkstra Direct Flights:")
        dijkstra_direct_flights_label.pack()
        for flight in self.results.dijkstra_direct_flights:
            flight_label = customtkinter.CTkLabel(scrollable_frame, text=f"Source: {flight['source']}, Destination: {flight['destination']}, Airline ID: {flight['airlineID']}")
            flight_label.pack()

        dijkstra_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame, text="Dijkstra Connecting Flights:")
        dijkstra_connecting_flights_label.pack()
        for flight in self.results.dijkstra_connecting_flights:
            flight_label = customtkinter.CTkLabel(scrollable_frame, text=f"Source: {flight['source']}, Destination: {flight['destination']}, Airline ID: {flight['airlineID']}")
            flight_label.pack()
            
        a_star_path_label = customtkinter.CTkLabel(scrollable_frame, text=f"A* Path: {' -> '.join(self.results.a_star_path_easy)}")
        a_star_path_label.pack()


        a_star_direct_flights_label = customtkinter.CTkLabel(scrollable_frame, text="A* Direct Flights:")
        a_star_direct_flights_label.pack()
        for flight in self.results.a_star_direct_flights:
            flight_label = customtkinter.CTkLabel(scrollable_frame, text=f"Source: {flight['source']}, Destination: {flight['destination']}, Airline ID: {flight['airlineID']}")
            flight_label.pack()

        a_star_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame, text="A* Connecting Flights:")
        a_star_connecting_flights_label.pack()
        for flight in self.results.a_star_connecting_flights:
            flight_label = customtkinter.CTkLabel(scrollable_frame, text=f"Source: {flight['source']}, Destination: {flight['destination']}, Airline ID: {flight['airlineID']}")
            flight_label.pack()
        
    def set_start_marker(self, start_iata):
        # Use geopy to get the coordinates of the start location based on the IATA code
        geolocator = Nominatim(user_agent="flightRouteMeasurements")
        start_location = geolocator.geocode(start_iata + " airport")

        if start_location:
            # Extract latitude and longitude
            start_lat, start_lon = start_location.latitude, start_location.longitude
            # Set marker on the map widget
            self.map_widget.set_marker(start_lat, start_lon)
            self.start_coordinate = (start_lat, start_lon)
        
    
    def set_destination_marker(self, destination_iata):
        # Use geopy to get the coordinates of the destination location based on the IATA code
        geolocator = Nominatim(user_agent="flightRouteMeasurements")
        destination_location = geolocator.geocode(destination_iata + " airport")

        if destination_location:
            # Extract latitude and longitude
            dest_lat, dest_lon = destination_location.latitude, destination_location.longitude
            # Set marker on the map widget
            self.map_widget.set_marker(dest_lat, dest_lon)
            self.destination_coordinate = (dest_lat, dest_lon)
             
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

    def calculate_zoom(self, distance):
        # Calculate the zoom level based on the distance
        # This is a simplified calculation, you may need to adjust it based on your map widget's specifications
        return round(14 - math.log2(distance / 360))

    # Search route from start to destination
    def search_event(self, event=None):
        
        # Retrieve input values
        start_iata = self.entry_start.get()
        destination_iata = self.entry_destination.get()

        if not start_iata or not destination_iata:
            self.status_code.configure(text_color="red")
            self.status_variable.set("Please enter both start and destination IATA codes!")
            return
        
        self.set_start_marker(start_iata)
        self.set_destination_marker(destination_iata)
        
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
        self.status_variable.set("Searching .... Please Wait...")
        self.update()
        
        # Perform search operation
        print("Search")

        self.planner = FlightPlanner(start_iata, destination_iata)
        self.planner.create_graph()
        self.results = self.planner.find_flights(start_iata, destination_iata)

        # For checking the "self.results" returned from line above
        # Attributes in the "self.results" object
        # dijkstra_time, dijkstra_time_unit, dijkstra_path, dijkstra_direct_flights, dijkstra_connecting_flights
        # a_star_time, a_star_time_unit, a_star_path, a_star_direct_flights, a_star_connecting_flights
        print(f"Dijkstra's algorithm time(empirical): {self.results.dijkstra_time} 'seconds'")
        print(f"Dijkstra's algorithm path: {self.results.dijkstra_path}")
        print(f"Dijkstra's algorithm total distance: {self.results.dijkstra_total_distance}")
        print(f"A* algorithm total cost: {self.results.dijkstra_total_cost}")
        print(f"Dijkstra's algorithm direct flights: {self.results.dijkstra_direct_flights}")
        print(f"Dijkstra's algorithm connecting flights: {self.results.dijkstra_connecting_flights}")
        
        print(f"A* algorithm time(empirical): {self.results.a_star_time} 'seconds'")
        print(f"A* algorithm path: {self.results.a_star_path}")
        print(f"A* algorithm total distance: {self.results.a_star_total_distance}")
        print(f"A* algorithm total cost: {self.results.a_star_total_cost}")
        print(f"A* algorithm direct flights: {self.results.a_star_direct_flights}")
        print(f"A* algorithm connecting flights: {self.results.a_star_connecting_flights}")
        
        # Do something with the input values
        print("Start IATA:", start_iata)
        print("Destination IATA:", destination_iata)

        self.status_code.configure(text_color="green")
        self.status_variable.set("Done!")

        
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