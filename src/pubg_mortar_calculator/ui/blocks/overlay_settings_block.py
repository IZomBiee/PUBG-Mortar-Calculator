import customtkinter as ct

from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock


class OverlaySettingsBlock(TitledBlock):
    def __init__(self, master, on_overlay_change, *args, **kwargs):
        super().__init__(master, "Overlay Settings", *args, **kwargs)
        grid = self.get_grid()

        grid.grid_columnconfigure((0, 1), weight=1)

        self.enabled_checkbox = Checkbox(
            grid,
            text="Enabled",
            saving_id="overlay_settings_enabled_checkbox",
            command=on_overlay_change,
        ).grid(row=0, column=0, padx=5, pady=5)

        self.draw_borders_checkbox = Checkbox(
            grid,
            text="Draw Borders",
            saving_id="overlay_settings_draw_borders_checkbox",
            command=on_overlay_change,
        ).grid(row=0, column=1, padx=5, pady=5)

        ct.CTkLabel(grid, text="App Title:").grid(row=1, column=0)

        self.title_entry = Entry(
            grid,
            text="PUBG:",
            saving_id="overlay_settings_title_entry",
            command=on_overlay_change,
        ).grid(row=1, column=1, padx=5, pady=5)

        self.scale_slider = Slider(
            grid,
            "Scale",
            "overlay_settings_scale_slider",
            50,
            250,
            100,
            command=on_overlay_change,
        )
        self.scale_slider.grid(row=2, columnspan=2, padx=5, pady=5)
