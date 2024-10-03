from email.errors import NonPrintableDefect

import customtkinter
from tkintermapview import TkinterMapView

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class App(customtkinter.CTk):
    APP_NAME = "RedAlertMapViewer"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = App.APP_NAME
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)

        self.market_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.left_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.right_frame = customtkinter.CTkFrame(master=self, corner_radius=0, fg_color=None)
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

    def set_market_event(self):
        return None

    def clear_marker_event(self):
        return None

    def change_appearance_mode(self):
        return None

    def change_map(self):
        return None


if __name__ == "__main__":
    app = App()
    app.mainloop()
