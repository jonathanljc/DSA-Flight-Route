import customtkinter
import time
from tkintermapview import TkinterMapView
from data import DataFilter
from routes import FlightGraph
from flightPlanner import FlightPlanner

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
        print("Additional Information")
        self.additional_window = customtkinter.CTkToplevel(self)
        self.additional_window.title("Additional Information")
        self.additional_window.geometry("600x600")
        self.additional_window.minsize(600, 600)
        
    # need to be changed
    def search_event(self, event=None):
        # Update status to indicate searching
        self.status_code.configure(text_color="red")
        self.status_variable.set("Searching .... Please Wait...")
        self.update()
        
        # Retrieve input values
        start_iata = self.entry_start.get()
        destination_iata = self.entry_destination.get()

        # Perform search operation
        print("Search")

        self.planner = FlightPlanner(start_iata, destination_iata)
        self.planner.create_graph()
        self.planner.find_flights(start_iata, destination_iata)
        
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
