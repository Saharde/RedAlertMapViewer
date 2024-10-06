import asyncio
import threading
from tkinter import EventType

import aiohttp
import customtkinter
import tkintermapview
from datetime import datetime
from tkintermapview.canvas_position_marker import CanvasPositionMarker
import tkinter
import geocoder

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

reverse = True


def get_location(address: str):
    location = None
    try:  # Try using Nominatim's geocoding
        location = tkintermapview.convert_address_to_coordinates(address)
        if not location:
            raise Exception()
    except Exception:  # Try using LocationIQ's geocoding
        print("Couldn't find it using the util func...")
        location = geocoder.locationiq(location=address, method="geocode", countrycodes="il", limit=1,
                                       key="YOUR_API_KEY_HERE")
        location = (location.lat, location.lng)
        print(location)

    return location


class RedAlertWindow(customtkinter.CTkToplevel):
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.configure(fg_color="red")

        self.red_alert_label = customtkinter.CTkLabel(master=self, text=title, font=("Helvetica", 120, "bold"))
        self.red_alert_label.pack(padx=20, pady=20, expand=True)

        self.attributes('-fullscreen', True)
        self.focus_force()


class App(customtkinter.CTk):
    APP_NAME = "RedAlertMapViewer"
    WIDTH = 800
    HEIGHT = 500

    json_url = "https://www.oref.org.il/warningMessages/alert/History/AlertsHistory.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)

        self.areas_of_interest_marker_list: list[CanvasPositionMarker] = []

        self.areas_of_interest: set[str] = set()

        self.alert_monitoring = True
        self.saved_alerts: dict[frozenset, customtkinter.CTkToplevel] = {}
        self.waiting_time_minutes = 58

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
            command=self.set_user_marker_event
        )
        self.set_market_button.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.clear_markers_button = customtkinter.CTkButton(
            master=self.left_frame,
            text="Clear Markers",
            command=self.clear_marker_event
        )
        self.clear_markers_button.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.areas_of_interest_textbox = customtkinter.CTkTextbox(
            master=self.left_frame,
            fg_color=('#F9F9FA', '#343638'),
            bg_color=('gray86', 'gray17'),
            text_color=('gray10', '#DCE4EE'),
            corner_radius=6,
            border_width=2,
            border_color=('#979DA2', '#565B5E')
        )
        self.areas_of_interest_textbox.grid(pady=(20, 0), padx=(20, 20), row=2, column=0, sticky="nsew")
        self.aoi_placeholder = customtkinter.CTkLabel(
            master=self.left_frame, text="type areas of interest:", text_color=('gray52', 'gray62'), anchor="nw",
            fg_color=('#F9F9FA', '#343638')
        )
        self.aoi_placeholder.place(in_=self.areas_of_interest_textbox, x=5, y=5)
        self.areas_of_interest_textbox.bind("<KeyRelease>", self.toggle_placeholder, "+")
        self.areas_of_interest_textbox.bind("<FocusIn>", self.toggle_placeholder, "+")
        self.areas_of_interest_textbox.bind("<FocusOut>", self.toggle_placeholder, "+")

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

        threading.Thread(target=self.start_monitoring_loop, daemon=True).start()

    def toggle_placeholder(self, event: tkinter.Event = None):
        current_text = self.areas_of_interest_textbox.get("1.0", "end-1c")
        if current_text == "" and event.type == EventType.FocusOut:
            self.aoi_placeholder.place(
                in_=self.areas_of_interest_textbox,
                x=5,
                y=5,
            )
        else:
            self.aoi_placeholder.place_forget()

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_user_marker_event(self):
        user_input = self.areas_of_interest_textbox.get("1.0", "end-1c")

        for area in user_input.split("\n"):
            if area in self.areas_of_interest:
                continue

            self.areas_of_interest.add(area)

            location = get_location(area)
            marker = self.map_widget.set_marker(location[0], location[1], marker_color_circle="#1e269b",
                                                marker_color_outside="#2d54c5")
            self.areas_of_interest_marker_list.append(marker)

    def clear_marker_event(self):
        for marker in self.areas_of_interest_marker_list:
            marker.delete()

        self.areas_of_interest.clear()
        self.areas_of_interest_textbox.delete("1.0", "end-1c")

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

    def start_monitoring_loop(self):
        asyncio.run(self.monitor_alerts())

    async def monitor_alerts(self):
        polling_interval = 1  # seconds, to ensure prompt alerts
        async with aiohttp.ClientSession() as session:
            while self.alert_monitoring:
                try:
                    async with session.get(App.json_url) as response:
                        if response.status == 200:
                            data = await response.json()

                            current_alerts = []
                            for alert in data:
                                if "מבואות חרמון" in alert['data'] or "דרום השרון" in alert['data']:
                                    alert['data'].replace('מועצה אזורית ', "")

                                if any(area in alert['data'] for area in self.areas_of_interest):
                                    current_alerts.append(alert)

                            for alert in current_alerts:
                                alert_time = datetime.strptime(alert['alertDate'], "%Y-%m-%d %H:%M:%S")
                                now_time = datetime.now()

                                difference_in_minutes = (now_time - alert_time).total_seconds() / 60

                                red_alert_window = self.saved_alerts.get(frozenset(alert.items()))
                                if not red_alert_window:
                                    if difference_in_minutes < self.waiting_time_minutes:
                                        print(f"{alert['title']} ב{alert['data']}")
                                        red_alert_window = RedAlertWindow(
                                            title=f"{alert['title']} ב{alert['data']}")
                                        self.saved_alerts[frozenset(alert.items())] = red_alert_window
                                else:
                                    if difference_in_minutes >= self.waiting_time_minutes:
                                        try:
                                            red_alert_window.destroy()
                                        except Exception as e:
                                            print(f"Error destroying \"{alert['data']}\" red alert window: {e}")
                                        del self.saved_alerts[frozenset(alert.items())]

                except aiohttp.ClientError as e:
                    print("end", f"Error fetching alerts: {e}\n")

                await asyncio.sleep(polling_interval)


if __name__ == "__main__":
    app = App()
    app.mainloop()
