import tkinter

from customtkinter.customtkinter_theme_manager import CTkThemeManager
from protonvpn_cli.country_codes import country_codes
from protonvpn_cli import connection
from traceback import format_exc
from contextlib import suppress
from PIL import Image, ImageTk
from threading import Thread
import customtkinter as ctk
from tkinter import Event
import json


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("./themes/monokai.json")    # theme can be changed


# load server positions
SERVER_POSITIONS: dict[str, list] = json.load(open("server_positions.json"))


class Window(ctk.CTk):
    servers_by_country: dict[str, list[dict]]
    map_country_icons: dict[str, int]
    map_current_hover: dict[str, int]
    vpn_protocol: str = "udp"
    map_drawn: bool = False
    map_shown: bool = False
    connected: bool = False
    connection_lines: list
    server_objects: list
    running: bool = True

    images: dict[str, ImageTk.PhotoImage]

    def __init__(self) -> None:
        super().__init__()

        # mutable defaults init
        self.servers_by_country = {}
        self.map_country_icons = {}
        self.map_current_hover = {}
        self.connection_lines = []
        self.server_objects = []

        button_icon_size = (32, 32)

        # load images
        self.images = {
            "speedometer": ImageTk.PhotoImage(Image.open("./icons/speedometer.png").resize(button_icon_size)),
            "triangle_hover": ImageTk.PhotoImage(Image.open("./icons/triangle.png").resize((24, 24))),
            "disconnect": ImageTk.PhotoImage(Image.open("./icons/disconnect.png").resize((24, 24))),
            "countries": ImageTk.PhotoImage(Image.open("./icons/countries.png").resize(button_icon_size)),
            "thunder": ImageTk.PhotoImage(Image.open("./icons/thunder.png").resize(button_icon_size)),
            "shield": ImageTk.PhotoImage(Image.open("./icons/shield.png").resize(button_icon_size)),
            "random": ImageTk.PhotoImage(Image.open("./icons/random.png").resize(button_icon_size)),
            "connect": ImageTk.PhotoImage(Image.open("./icons/link.png").resize(button_icon_size)),
            "triangle": ImageTk.PhotoImage(Image.open("./icons/triangle.png").resize((12, 12))),
            "lock": ImageTk.PhotoImage(Image.open("./icons/lock.png").resize(button_icon_size)),
            "tor": ImageTk.PhotoImage(Image.open("./icons/tor.png").resize(button_icon_size)),
            "p2p": ImageTk.PhotoImage(Image.open("./icons/p2p.png").resize(button_icon_size)),
            "map": ImageTk.PhotoImage(Image.open("./icons/worldmap.png").resize((1000, 500))),
            "map_orig": Image.open("./icons/worldmap.png"),
        }

        # configure window
        self.title("Proton VPN")
        self.geometry("400x720")
        # self.minsize(width=400, height=720)
        self.resizable(True, True)

        self.protocol("WM_DELETE_WINDOW", self.end)
        self.bind("<Alt-Key-F4>", self.end)
        self.bind("<Escape>", self.end)

        # create widgets
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.map_canvas = ctk.CTkCanvas(
            self,
            bg=CTkThemeManager.theme["color"]["window_bg_color"][0],
            highlightthickness=0,
        )
        self.map_canvas.bind("<Configure>", lambda _e: self.draw_map_locations())
        self.map_canvas.bind("<Motion>", self.check_map_hover)

        self.default_view = ctk.CTkFrame(self, width=400)
        self.default_view.grid_propagate(False)
        self.default_view.grid(row=0, column=0, sticky="nsew")

        self.default_view.grid_rowconfigure(list(range(2)), weight=1)
        self.default_view.grid_rowconfigure(list(range(3, 6)), weight=1)
        self.default_view.grid_columnconfigure(list(range(3)), weight=1)

        self.current_plan = ctk.CTkLabel(self.default_view, text="Server Features: ")
        self.current_plan.grid(row=2, column=0, columnspan=3)

        self.status_frame = ctk.CTkFrame(self.default_view)
        self.status_frame.grid(row=0, column=0, rowspan=2, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.status_frame.grid_rowconfigure(list(range(5)), weight=1)
        self.status_frame.grid_columnconfigure(list(range(10)), weight=1)

        self.connection_label = ctk.CTkLabel(
            self.status_frame,
            text="No connection!",
            text_color="red",
            text_font=("Roboto Medium", -20),
        )
        self.connection_label.grid(row=0, column=0, columnspan=10, sticky="nsew", padx=10, pady=5)
        self.connection_label.text_label.grid(row=0, column=0, sticky="w")

        self.ip_label = ctk.CTkLabel(self.status_frame, text="IP:", text_font=("DejaVu Sans Light", -18))
        self.ip_label.grid(row=1, column=0, columnspan=7, sticky="nsew", padx=10)
        self.ip_label.text_label.grid(row=0, column=0, sticky="w")

        self.load_label = ctk.CTkLabel(self.status_frame, text="", text_font=("DejaVu Sans Light", -18))
        self.load_label.grid(row=1, column=7, columnspan=3, sticky="nsew", padx=10)
        self.load_label.text_label.grid(row=0, column=0, sticky="e")

        self.connection_type_label = ctk.CTkLabel(self.status_frame, text="", text_font=("DejaVu Sans Light", -15))
        self.connection_type_label.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10)
        self.connection_type_label.text_label.grid(row=0, column=0, sticky="we")

        self.rx_tx_label = ctk.CTkLabel(self.status_frame, text="", text_font=("DejaVu Sans Light", -15))
        self.rx_tx_label.grid(row=2, column=3, columnspan=7, sticky="nsew", padx=10)
        self.rx_tx_label.text_label.grid(row=0, column=0, sticky="e")

        self.connect_button = ctk.CTkButton(
            self.status_frame,
            text="Connect",
            height=40,
            text_font=("Roboto Medium", -20),
        )
        self.connect_button.grid(row=3, column=1, rowspan=2, columnspan=8, sticky="ew")

        self.servers_frame = ctk.CTkFrame(self.default_view)
        self.servers_frame.grid(row=3, column=0, rowspan=5, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.servers_frame.grid_rowconfigure(list(range(6)), weight=1)
        self.servers_frame.grid_columnconfigure(list(range(1)), weight=1)

        c_b_padding = 10

        self.connect_random_button = ctk.CTkButton(
            self.servers_frame,
            text="Random",
            command=lambda *_e: connection.random_c(protocol=self.vpn_protocol),
            image=self.images["random"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_random_button.grid(row=0, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        self.connect_country_button = ctk.CTkButton(
            self.servers_frame,
            text="Map",
            command=lambda *_e: self.hide_map() if self.map_shown else self.show_map(),
            image=self.images["countries"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_country_button.grid(row=1, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        self.connect_overall_fastest_button = ctk.CTkButton(
            self.servers_frame,
            text="Fastest",
            command=lambda *_e: connection.fastest(protocol=self.vpn_protocol),
            image=self.images["speedometer"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_overall_fastest_button.grid(row=2, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        self.connect_secure_core_fastest_button = ctk.CTkButton(
            self.servers_frame,
            text="Secure Core",
            command=lambda *_e: connection.feature_f(1),
            image=self.images["shield"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_secure_core_fastest_button.grid(row=3, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        self.connect_p2p_fastest_button = ctk.CTkButton(
            self.servers_frame,
            text="Pier 2 Pier",
            command=lambda *_e: connection.feature_f(4),
            image=self.images["p2p"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_p2p_fastest_button.grid(row=4, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        self.connect_tor_fastest_button = ctk.CTkButton(
            self.servers_frame,
            text="Tor",
            command=lambda *_e: connection.feature_f(2),
            image=self.images["tor"],
            compound="image_left",
            # corner_radius=40,
        )
        self.connect_tor_fastest_button.grid(row=5, column=0, sticky="nsew", padx=c_b_padding, pady=c_b_padding)

        # start threads
        Thread(target=self._update_status).start()

    def _update_status(self) -> None:
        while self.running:
            try:
                middle = (
                    self.map_canvas.winfo_width() / 2,
                    self.map_canvas.winfo_height() / 2,
                )

                vpn_status = connection.status()
                self.connected = vpn_status["connected"]

                if self.connected:
                    for line in self.connection_lines:
                        self.map_canvas.delete(line)

                    self.connection_lines.clear()

                    if self.map_shown:
                        if vpn_status["features"] == "Secure-Core":
                            print("drawing secure core")
                            route = vpn_status["server"].split("#")[0].split("-")
                            c1 = country_codes[route[0].upper()]
                            c2 = country_codes[route[1].upper()]

                            s1 = SERVER_POSITIONS[c1.lower()]
                            s2 = SERVER_POSITIONS[c2.lower()]

                            self.connection_lines.append(self.map_canvas.create_line(middle[0], middle[1] * .2,
                                                                                     middle[0] + s1[0],
                                                                                     middle[1] + s1[1],
                                                                                     fill="#ac3dff"))

                            self.connection_lines.append(self.map_canvas.create_line(middle[0] + s1[0],
                                                                                     middle[1] + s1[1],
                                                                                     middle[0] + s2[0],
                                                                                     middle[1] + s2[1],
                                                                                     fill="#ac3dff",
                                                                                     width=3))

                            print(f"new: {self.connection_lines}")

                        else:
                            server_pos = SERVER_POSITIONS[vpn_status["country"].lower()]

                            self.connection_lines.append(self.map_canvas.create_line(middle[0], middle[1] * .2,
                                                         middle[0]+server_pos[0], middle[1]+server_pos[1],
                                                         fill="#322a55", width=2))

                            self.connection_lines.append(self.map_canvas.create_line(middle[0], middle[1] * .2,
                                                         middle[0]+server_pos[0], middle[1]+server_pos[1],
                                                         fill="#967eff", width=1))

                    self.current_plan.configure(text=f"Features: {vpn_status['features']}")
                    self.connection_label.configure(
                        text=f"{vpn_status['country']} {vpn_status['server']}",
                        text_color="white"
                    )

                    self.ip_label.configure(text=f"IP: {vpn_status['ip']}")
                    self.load_label.configure(text=f"{vpn_status['load']}% Load")
                    self.connection_type_label.configure(text=vpn_status["protocol"])
                    self.rx_tx_label.configure(text=f"{vpn_status['received']} ↓  {vpn_status['sent']} ↑ ")

                    self.connect_button.configure(
                        text="Disconnect",
                        command=lambda *_e: Thread(target=connection.disconnect()).start(),
                        image=self.images["disconnect"],
                    )

                    continue

                self.connection_label.configure(text="You are not connected", text_color="brown1")
                self.connect_button.configure(
                    text="Reconnect",
                    command=lambda *_e: Thread(target=connection.reconnect()).start(),
                    image=self.images["connect"],
                )

                self.ip_label.configure(text=f"IP:")
                self.load_label.configure(text="")
                self.connection_type_label.configure(text="")
                self.rx_tx_label.configure(text="")

            except Exception:
                print(f"error in thread 1: {format_exc()}")
                raise

    def draw_map_locations(self) -> None:
        """
        draw (known) server locations on map
        """
        self.update()   # force update
        print(f"redrawing map")
        for line in self.connection_lines:
            self.map_canvas.delete(line)

        for o in self.server_objects:
            self.map_canvas.delete(o)

        self.server_objects.clear()

        # redraw the actual landmass
        # self.images["map"] = ...

        img = self.map_canvas.create_image(
            self.map_canvas.winfo_width() / 2,
            self.map_canvas.winfo_height() / 2,
            image=self.images["map"]
        )

        self.server_objects.append(img)

        # redraw the servers
        middle = (
            self.map_canvas.winfo_width() / 2,
            self.map_canvas.winfo_height() / 2,
        )

        servers = connection.get_servers()
        self.servers_by_country.clear()

        for server in servers:
            # return
            cc = server["Name"][:2]
            country = country_codes[cc.upper()]

            if country not in self.servers_by_country:
                self.map_canvas.tag_bind(country, "<Button-1>", lambda e, code=cc: self.should_connect(e, code))
                self.servers_by_country[country] = []

            self.servers_by_country[country].append(server)

        total_size = len(list(self.servers_by_country.keys()))
        done = 0
        for country in self.servers_by_country.keys():
            try:
                pos = SERVER_POSITIONS[country.lower()]

                x = middle[0] + pos[0]
                y = middle[1] + pos[1]

                im = self.map_canvas.create_image(x, y, image=self.images["triangle"], tags=(country, country+"HOVER"))
                self.map_country_icons[country+"HOVER"] = im
                self.server_objects.append(im)
                done += 1

            except KeyError:
                print(f"{done}/{total_size} - not in list: {country.lower()}")
                raise

        self.map_drawn = True

    def check_map_hover(self, _event) -> None:
        """
        check if the mouse hovers over an icon (map)
        """
        middle = (
            self.map_canvas.winfo_width() / 2,
            self.map_canvas.winfo_height() / 2,
        )

        tags = self.map_canvas.gettags("current")
        for tag in tags:
            if tag in self.map_country_icons:
                self.map_canvas.delete(self.map_country_icons[tag])

                country = tag.rstrip("HOVER")

                pos = SERVER_POSITIONS[country.lower()]

                x = middle[0] + pos[0]
                y = middle[1] + pos[1]

                im = self.map_canvas.create_image(x, y, image=self.images["triangle_hover"],
                                                  tags=(country, country+"HOVER"))
                self.map_country_icons[tag] = im
                self.map_current_hover[tag] = im
                self.server_objects.append(im)

        for tag in set(self.map_current_hover.keys()) - set(tags):
            t_id = self.map_current_hover.pop(tag)
            self.map_canvas.delete(t_id)

            country = tag.rstrip("HOVER")

            pos = SERVER_POSITIONS[country.lower()]

            x = middle[0] + pos[0]
            y = middle[1] + pos[1]

            im = self.map_canvas.create_image(x, y, image=self.images["triangle"],
                                              tags=(country, country + "HOVER"))
            self.map_country_icons[tag] = im
            self.server_objects.append(im)

    def show_map(self) -> None:
        """
        show the connection map
        """
        self.map_shown = True
        self.map_canvas.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.geometry("1500x720")

        self.update()

        self.draw_map_locations()

    def hide_map(self) -> None:
        """
        hide the connection map
        """
        self.map_shown = False
        self.map_canvas.grid_forget()
        self.geometry("400x720")

    def should_connect(self, event: Event, country_code: str) -> None:
        """
        popup asking if you should connect to the country or not
        """
        country = country_codes[country_code]

        con_window = ctk.CTkToplevel(self.map_canvas, bg="#292733")
        con_window.wm_overrideredirect(True)

        x = self.winfo_x() + self.map_canvas.winfo_x() + event.x - 100
        y = self.winfo_y() + self.map_canvas.winfo_y() + event.y - 124
        con_window.geometry(f"200x100+{x}+{y}")

        con_window.grid_rowconfigure([0, 1], weight=1)
        con_window.grid_columnconfigure(0, weight=1)

        def destroy_toplevel():
            con_window.destroy()
            con_window.update()

        con_window.bind("<FocusOut>", lambda _e: destroy_toplevel())

        lab = ctk.CTkLabel(con_window, text=country, text_font=("Roboto Medium", -18))
        but = ctk.CTkButton(con_window, text="Connect", fg_color="#06b300", text_font=("Roboto Medium", -17),
                            command=lambda cc=country_code: connection.country_f(cc))

        lab.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)
        but.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)

        con_window.focus_set()

    def run(self) -> None:
        """
        run the mainloop
        """
        self.mainloop()

    def end(self, *_trash) -> None:
        """
        close the instance and all running threads
        """
        print(f"closing")
        self.running = False

        with suppress(Exception):
            self.destroy()

        print("exiting")
        exit(0)


def main():
    w = Window()
    w.run()
    w.end()


if __name__ == "__main__":
    main()
