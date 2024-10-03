import customtkinter
import tkintermapview

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class App(customtkinter.CTk):
    APP_NAME = "RedAlertMapViewer"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)

        self.marker_list: list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.left_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.right_frame = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.right_frame.grid(row=0, column=1, rowspan=1, padx=0, pady=0, sticky="nsew")

        # ============ left_frame ============

        self.left_frame.grid_rowconfigure(2, weight=1)

        self.set_market_button = customtkinter.CTkButton(
            master=self.left_frame,
            text="Set Marker",
            command=self.set_market_event
        )
        self.set_market_button.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.clear_markers_button = customtkinter.CTkButton(
            master=self.left_frame,
            text="Clear Markers",
            command=self.clear_marker_event
        )
        self.clear_markers_button.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.tile_server_label = customtkinter.CTkLabel(master=self.left_frame, text="Tile Server:", anchor="w")
        self.tile_server_label.grid(row=3, column=0, padx=(20, 20), pady=(20, 0))
        self.tile_server_option_menu = customtkinter.CTkOptionMenu(
            master=self.left_frame,
            values=["OpenStreetMap", 'Google Maps Normal', "Google Maps Satellite"],
            command=self.change_map
        )
        self.tile_server_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(master=self.left_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(
            master=self.left_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

        # ============ right_frame ============

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=0)
        self.right_frame.grid_columnconfigure(2, weight=1)

        self.map_widget = tkintermapview.TkinterMapView(
            master=self.right_frame,
            corner_radius=0
        )
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.right_frame, placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.search_button = customtkinter.CTkButton(
            master=self.right_frame,
            text="Search",
            width=90,
            command=self.search_event
        )
        self.search_button.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # ============ Set default values ============
        self.map_widget.set_address("Jerusalem")
        self.tile_server_option_menu.set("OpenStreetMap")
        self.appearance_mode_option_menu.set("System")

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_market_event(self):
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
        elif new_map == "Google Maps Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)
        elif new_map == "Google Maps Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)


if __name__ == "__main__":
    app = App()
    app.mainloop()
