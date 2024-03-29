import customtkinter
import time
import math
import gettext
import os
from tkintermapview import TkinterMapView
from data import DataFilter
from routes import FlightGraph
from flightPlanner import FlightPlanner
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from tkinter import ttk # For tabs
import locale

# Set the locale to the user's default setting
locale.setlocale(locale.LC_ALL, '')

# Get the current locale and encoding
current_locale = locale.getlocale()
encoding = locale.getpreferredencoding()

locale_path = 'locales'
language = gettext.translation('base', localedir=locale_path, languages=['en'], fallback=True)
language.install()
_ = language.gettext



customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):

    APP_NAME = _("Flight Map Routing System")
    WIDTH = 1000
    HEIGHT = 700

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
        self.selected_algorithm = customtkinter.StringVar(value=_("Dijkstra"))

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(12, weight=1)
        
        self.map_label = customtkinter.CTkLabel(self.frame_left, text=_("Tile Server:"), anchor="w")
        self.map_label.grid(row=0, column=0, padx=(20, 20), pady=(10, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=[_("OpenStreetMap"), _("Google normal"), _("Google satellite")],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text=_("Appearance Mode:"), anchor="w")
        self.appearance_mode_label.grid(row=2, column=0, padx=(20, 20), pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=[_("Light"), _("Dark"), _("System")],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))
        
        self.label_start = customtkinter.CTkLabel(self.frame_left, text=_("Start (IATA Code):"), anchor="w")
        self.label_start.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))

        self.entry_start = customtkinter.CTkEntry(self.frame_left, placeholder_text=_("Enter start IATA"))
        self.entry_start.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.label_destination = customtkinter.CTkLabel(self.frame_left, text=_("Destination (IATA Code):"), anchor="w")
        self.label_destination.grid(row=6, column=0, padx=(20, 20), pady=(10, 0))

        self.entry_destination = customtkinter.CTkEntry(self.frame_left, placeholder_text=_("Enter destination IATA"))
        self.entry_destination.grid(row=7, column=0, padx=(20, 20), pady=(10, 0))


        self.algorithm_label = customtkinter.CTkLabel(self.frame_left, text=_("Choose Path:"), anchor="w")
        self.algorithm_label.grid(row=8, column=0, padx=(20, 20), pady=(10, 0))
        self.algorithm_optionmenu = customtkinter.CTkOptionMenu(self.frame_left, values=[_("Dijkstra"), _("A*"), _("Bellman-Ford"), _("Cheapest Path")],
                                                                       command=self.change_algorithm)
        self.algorithm_optionmenu.grid(row=9, column=0, padx=(20, 20), pady=(10, 0))


        self.search_button = customtkinter.CTkButton(master=self.frame_left,
                                                text=_("Search"),
                                                command=self.search_event)
        self.search_button.grid(row=10, column=0, padx=(20, 20), pady=(30, 0))
        
        self.status_label = customtkinter.CTkLabel(self.frame_left, 
                                                   text=_("Status:"))
        self.status_label.grid(row=11, column=0, padx=(20, 20), pady=(45, 0))
        
        self.status_code = customtkinter.CTkLabel(self.frame_left, textvariable=self.status_variable, wraplength=140, justify="center")
        self.status_code.grid(row=12, column=0, padx=(10, 10), pady=(1, 0))


        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(0, weight=95)
        self.frame_right.grid_rowconfigure(1, weight=5)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.additional_button = customtkinter.CTkButton(master=self.frame_right,
                                                 text=_("Search Results"),
                                                 command=self.open_additional_window)
        self.additional_button.grid(row=1, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew", columnspan=3)


        # Set default values
        self.map_var = customtkinter.StringVar(value=_("Google normal"))
        self.map_widget.set_address(_("Singapore"))
        self.map_option_menu.set(_("Google normal"))
        self.appearance_mode_optionemenu.set(_("System"))
        self.status_code.configure(text_color="green")
        self.status_variable.set(_("Ready!"))

        # ============ Additional Features ============

        self.language_label = customtkinter.CTkLabel(self.frame_left, text="Language:", anchor="w")
        self.language_label.grid(row=100, column=0, sticky='s', pady=(0, 20))  # Adjust row number and padding as needed

        self.language_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                values=["English", "中文 (Simplified Chinese)"],
                                                                command=self.change_language)
        self.language_option_menu.grid(row=101, column=0, sticky='s', pady=(0, 20))  # Adjust row number and padding as needed
        # Create StringVar instances to keep track of option menu selections
        # Add these lines after initializing the OptionMenu widgets
        self.map_var = customtkinter.StringVar(value=_("Google normal"))  # Default value
        self.appearance_mode_var = customtkinter.StringVar(value=_("System"))  # Default value

        # Use the StringVar instances with the OptionMenus
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                           variable=self.map_var,
                                                           values=[_("OpenStreetMap"), _("Google normal"), _("Google satellite")],
                                                           command=self.change_map)
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       variable=self.appearance_mode_var,
                                                                       values=[_("Light"), _("Dark"), _("System")],
                                                                       command=self.change_appearance_mode)
        self.change_map(self.map_var.get())

    def init_language(self, lang_code):
        global _
        try:
            lang = gettext.translation('base', localedir=locale_path, languages=[lang_code])
        except Exception:
            lang = gettext.NullTranslations()
        lang.install()
        _ = lang.gettext
        self.refresh_ui()

    def change_language(self, selection):
        # Map selections to language codes
        lang_codes = {"English": "en", "中文 (Simplified Chinese)": "zh_CN"}
        self.init_language(lang_codes.get(selection, "en"))

    def change_algorithm(self, algorithm):
        self.selected_algorithm.set(algorithm)

    def set_default_values(self):
        self.map_var = customtkinter.StringVar(value=_("Google normal"))
        self.appearance_mode_var = customtkinter.StringVar(value=_("System"))

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                           variable=self.map_var,
                                                           values=[_("OpenStreetMap"), _("Google normal"), _("Google satellite")],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       variable=self.appearance_mode_var,
                                                                       values=[_("Light"), _("Dark"), _("System")],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))

        # Call to update the UI text
        self.refresh_ui()
    
    def refresh_ui(self):
        self.title(_("Flight Map Routing System"))  # Update window title
        
        # Update the text for all labels, buttons, etc.
        self.search_button.configure(text=_("Search"))
        self.label_start.configure(text=_("Start (IATA Code):"))
        self.label_destination.configure(text=_("Destination (IATA Code):"))
        self.map_label.configure(text=_("Tile Server:"))
        self.appearance_mode_label.configure(text=_("Appearance Mode:"))
        self.status_label.configure(text=_("Status:"))
        self.additional_button.configure(text=_("Search Results"))
        self.language_label.configure(text=_("Language:"))

        self.update_option_menu(self.map_option_menu, self.map_var, ["OpenStreetMap", "Google normal", "Google satellite"])
        self.update_option_menu(self.appearance_mode_optionemenu, self.appearance_mode_var, [_("Light"), _("Dark"), _("System")])
        
        # Update the variable text if used in labels or elsewhere
        self.status_variable.set(_("Ready!"))

        # Force a redraw of the UI to reflect changes
        self.update_idletasks()


    def update_option_menu(self, option_menu_attr_name, var, new_values):
        # Define current_value at the beginning of the method
        current_value = var.get()

        # Check and destroy the existing CTkOptionMenu widget
        if hasattr(self, option_menu_attr_name):
            getattr(self, option_menu_attr_name).destroy()

        # Create a new CTkOptionMenu with the updated options
        new_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                    variable=var,
                                                    values=new_values,
                                                    command=self.change_map)
        setattr(self, option_menu_attr_name, new_option_menu)

        # Place the new CTkOptionMenu in the UI
        getattr(self, option_menu_attr_name).grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        # Restore the previous selection or default to the first option
        var.set(current_value if current_value in new_values else new_values[0])

    # additional window for displaying all search information
    def open_additional_window(self):
        
        if self.status_variable.get() != _("Search Completed!"):
            self.status_code.configure(text_color="red")
            self.status_variable.set(_("Please search for flights first!"))
            return
        
        print("Additional Information")
        self.additional_window = customtkinter.CTkToplevel(self)
        self.additional_window.title(_("Additional Information"))
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
        notebook.add(tab1, text=_('Dijkstra Algorithm'))
        notebook.add(tab2, text=_('A* Algorithm'))
        notebook.add(tab3, text=_('Bellman-Ford Algorithm'))

        
        # Create a scrollable frame with a black background
        scrollable_frame = customtkinter.CTkScrollableFrame(tab1, bg_color="black", label_text=_("Search Results"))
        scrollable_frame.pack(fill="both", expand=True)

        # Second scrollable frame
        scrollable_frame2 = customtkinter.CTkScrollableFrame(tab2, bg_color="black", label_text=_("Search Results"))
        scrollable_frame2.pack(fill="both", expand=True)

        # Third scrollable frame
        scrollable_frame3 = customtkinter.CTkScrollableFrame(tab3, bg_color="black", label_text=_("Search Results"))
        scrollable_frame3.pack(fill="both", expand=True)
        
        # Create labels to display information
        dijkstra_path_label = customtkinter.CTkLabel(scrollable_frame, text=_("Dijkstra Path: {}").format(' -> '.join(self.results.dijkstra_all_paths[0])))
        dijkstra_path_label.pack()

        # Display the Dijkstra algorithm path
        for index, segment in enumerate(self.results.dijkstra_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame, text=_(f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)"))
            path_label.pack()

        # Display total distance for Dijkstra's algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame, text=_(f"Total Distance: {self.results.dijkstra_total_distance:.2f} km"))
        total_distance_label.pack()

        # Create labels to display information for A* algorithm
        a_star_path_label = customtkinter.CTkLabel(scrollable_frame2, text=_(f"A* Path: {' -> '.join(self.results.a_star_all_paths[0])}"))
        a_star_path_label.pack()

        # Display the A* algorithm path
        for index, segment in enumerate(self.results.a_star_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame2, text=_(f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)"))
            path_label.pack()

        # Display total distance for A* algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame2, text=_(f"Total Distance (A*): {self.results.a_star_total_distance:.2f} km"))
        total_distance_label.pack()


        # Create labels to display information for Bellman-Ford algorithm
        bellman_ford_path_label = customtkinter.CTkLabel(scrollable_frame3, text=_(f"Bellman Ford Path: {' -> '.join(self.results.bellman_ford_all_paths[0])}"))
        bellman_ford_path_label.pack()

        # Display the Bellman Ford algorithm path
        for index, segment in enumerate(self.results.bellman_ford_path):
            location1, location2, distance = segment
            path_label = customtkinter.CTkLabel(scrollable_frame3, text=_(f"{index+1}. {location1} -> {location2} (Distance: {distance:.2f} km)"))
            path_label.pack()

        # Display total distance for Bellman Ford algorithm
        total_distance_label = customtkinter.CTkLabel(scrollable_frame3, text=_(f"Total Distance (Bellman Ford): {self.results.bellman_ford_total_distance:.2f} km"))
        total_distance_label.pack()

        # Show Warning if Direct and Connecting Flights is unable to reach destination based on Calculated Path
        if self.results.dijkstra_valid_travel == 0:
            dijkstra_connecting_warning_label = customtkinter.CTkLabel(
                scrollable_frame, 
                text=_("WARNING: UNABLE TO REACH DESTINATION BASED ON PATH\n(No valid commercial flights routes)"),
                fg_color="red")
            dijkstra_connecting_warning_label.pack()

        if self.results.a_star_valid_travel == 0:
            a_star_connecting_warning_label = customtkinter.CTkLabel(
                scrollable_frame2, 
                text=_("WARNING: UNABLE TO REACH DESTINATION BASED ON PATH\n(No valid commercial flights routes)"),
                fg_color="red")
            a_star_connecting_warning_label.pack()
        
        if self.results.bellman_ford_valid_travel == 0:
            bellman_ford_connecting_warning_label = customtkinter.CTkLabel(
                scrollable_frame3, 
                text=_("WARNING: UNABLE TO REACH DESTINATION BASED ON PATH\n(No valid commercial flights routes)"),
                fg_color="red")
            bellman_ford_connecting_warning_label.pack()

        
        # Display the cheapest path for Dijkstra's algorithm
        cheapest_path_label = customtkinter.CTkLabel(scrollable_frame, text=_(f"Cheapest Path: "))
        cheapest_path_label.pack()
        
        # Create a dictionary to store the cheapest flight for each unique combination of source and destination
        flights = self.results.dijkstra_connecting_flights
        cheapest_flights = self.planner.calculate_cheapest_flights(flights)

        # Display the cheapest flights
        for flight in cheapest_flights.values():
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                command=None,
                )
            flight_button.pack(pady=5)
                
        # Display dijkstra direct and connecting flights
        dijkstra_direct_flights_label = customtkinter.CTkLabel(scrollable_frame, text=_("Direct Flights:"))
        dijkstra_direct_flights_label.pack()
        if len(self.results.dijkstra_direct_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text=_("No direct flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.dijkstra_direct_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)
            
        dijkstra_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame, text=_("Connecting Flights:"))
        dijkstra_connecting_flights_label.pack()
        if len(self.results.dijkstra_connecting_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame, 
                text=_("No connecting flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.dijkstra_connecting_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)
            
        # Display a_star direct and connecting flights
        a_star_direct_flights_label = customtkinter.CTkLabel(scrollable_frame2, text=_("Direct Flights:"))
        a_star_direct_flights_label.pack()
        if len(self.results.a_star_direct_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame2, 
                text=_("No direct flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.a_star_direct_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame2, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)
            
        a_star_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame2, text=_("Connecting Flights:"))
        a_star_connecting_flights_label.pack()
        if len(self.results.a_star_connecting_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame2, 
                text=_("No connecting flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.a_star_connecting_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame2, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)

        # Display bellman_ford direct and connecting flights
        bellman_ford_direct_flights_label = customtkinter.CTkLabel(scrollable_frame3, text=_("Direct Flights:"))
        bellman_ford_direct_flights_label.pack()
        if len(self.results.bellman_ford_direct_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame3, 
                text=_("No direct flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.bellman_ford_direct_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame3, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)
            
        bellman_ford_connecting_flights_label = customtkinter.CTkLabel(scrollable_frame3, text=_("Connecting Flights:"))
        bellman_ford_connecting_flights_label.pack()
        if len(self.results.bellman_ford_connecting_flights) == 0:
            flight_button = customtkinter.CTkButton(
                scrollable_frame3, 
                text=_("No connecting flights available"), 
                command=None,
                )
            flight_button.pack(pady=5)
        else:  
            for flight in self.results.bellman_ford_connecting_flights:
                flight_button = customtkinter.CTkButton(
                    scrollable_frame3, 
                    text=_(f"{flight['source']} ---------> {flight['destination']}\t{flight['airlineName']}\t\t${flight['price']}"), 
                    command=None,
                    )
                flight_button.pack(pady=5)
        
        # Add a button to close the additional window
        close_button = customtkinter.CTkButton(self.additional_window, text=_("Close"), command=self.additional_window.destroy)
        close_button.grid()
        
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
                    self.show_error_message(_(f"Start location ({start_iata}) is not a valid airport in Asia."))
                    self.start_coordinate = None
                    self.map_widget.set_position(start_lat, start_lon)
                    self.map_widget.set_zoom(3)
                    self.update()
                    return 
                
                self.start_coordinate = (start_lat, start_lon)
        
        except GeocoderTimedOut:
            self.show_error_message(_("Geocoding service timed out while fetching start location."))

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
                    self.show_error_message(_(f"Destination location ({destination_iata}) is not a valid airport in Asia."))
                    self.destination_coordinate = None
                    self.map_widget.set_position(dest_lat, dest_lon)
                    self.map_widget.set_zoom(3)
                    self.update()
                    return
                
                self.destination_coordinate = (dest_lat, dest_lon)
                
        except GeocoderTimedOut:
            self.show_error_message(_("Geocoding service timed out while fetching destination location."))
   
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
            self.status_variable.set(_("Searching Routes, Please Wait..."))
            self.update()
            
            # Perform search operation
            print(_("Search"))

            self.planner = FlightPlanner(start_iata, destination_iata)
            self.planner.create_graph()
            self.results = self.planner.find_flights(start_iata, destination_iata)

            print(_(f"Dijkstra's algorithm time(empirical): {self.results.dijkstra_time} 'seconds'"))
            print(_(f"Dijkstra's algorithm path: {self.results.dijkstra_path}"))
            print(_(f"Dijkstra's algorithm total distance: {self.results.dijkstra_total_distance}"))
            print(_(f"Dijkstra's algorithm total cost: {self.results.dijkstra_total_cost}"))
            print(_(f"Dijkstra's algorithm all paths: {self.results.dijkstra_all_paths}"))
            print(_(f"Dijkstra's algorithm all explored paths: {self.results.dijkstra_total_cost_path}"))

            print(_(f"A* algorithm time(empirical): {self.results.a_star_time} 'seconds'"))
            print(_(f"A* algorithm path: {self.results.a_star_path}"))
            print(_(f"A* algorithm total distance: {self.results.a_star_total_distance}"))
            print(_(f"A* algorithm total cost: {self.results.a_star_total_cost}"))
            print(_(f"A* algorithm all paths: {self.results.a_star_all_paths}"))
            print(_(f"A* algorithm all explored paths: {self.results.a_star_total_cost_path}"))

            print(_(f"Bellman-Ford algorithm time(empirical): {self.results.bellman_ford_time} 'seconds'"))
            print(_(f"Bellman-Ford algorithm path: {self.results.bellman_ford_path}"))
            print(_(f"Bellman-Ford algorithm total distance: {self.results.bellman_ford_total_distance}"))
            print(_(f"Bellman-Ford algorithm total cost: {self.results.bellman_ford_total_cost}"))
            print(_(f"Bellman-Ford algorithm all paths: {self.results.bellman_ford_all_paths}"))
            print(_(f"Bellman-Ford algorithm all explored paths: {self.results.bellman_ford_all_total_cost_path}"))
            
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
            print(_("Start IATA:"), start_iata)
            print(_("Destination IATA:"), destination_iata)
            
            # Set markers and paths for the Dijkstra path    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if self.selected_algorithm.get() == "Dijkstra":
                path_markers = self.setMarkersAndPaths(self.results.dijkstra_path)
            elif self.selected_algorithm.get() == "A*":
                path_markers = self.setMarkersAndPaths(self.results.a_star_path)
            elif self.selected_algorithm.get() == "Bellman-Ford":
                path_markers = self.setMarkersAndPaths(self.results.bellman_ford_path)
            elif self.selected_algorithm.get() == "Cheapest Path": # Edit
                flights = self.results.dijkstra_connecting_flights
                cheapest_flights = self.planner.calculate_cheapest_flights(flights)
                # Create a list of vertices for the cheapest flights path
                cheapest_flights_list = []
                for flight in cheapest_flights.values():
                    cheapest_flights_list.append((flight['source'], flight['destination'], flight['price']))

                path_markers = self.setMarkersAndPaths(cheapest_flights_list)

            self.status_code.configure(text_color="green")
            self.status_variable.set(_("Search Completed!"))
            self.update()
            
        except Exception as e:
            # Handle the error
            print(_("An error occurred:"), e)
            self.status_code.configure(text_color="red")
            self.status_variable.set(_("An error occurred during the search."))
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
                self.show_error_message(_(f"Geocoding service timed out while fetching coordinates for {location1} or {location2}."))
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
                    self.show_error_message(_(f"An error occurred while setting markers or path: {str(e)}"))
                    return

        # Return the list of markers and paths
        return path_markers
    
    def show_error_message(self, message):
        # Create a new top-level window for the error message
        error_window = customtkinter.CTkToplevel(self)
        error_window.title(_("Error"))
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
            self.map_widget.set_tile_server(_("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"))
        elif new_map == "Google normal":
            self.map_widget.set_tile_server(_("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga"), max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server(_("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga"), max_zoom=22)

    def on_closing(self, event=0):
        if self.additional_window:
            self.additional_window.destroy()  # Close the additional window if it exists

        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    # app.change_language("English")
    app.start()