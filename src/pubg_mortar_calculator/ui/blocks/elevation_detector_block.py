import customtkinter as ct

from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock


class ElevationDetectorBlock(TitledBlock):
    def __init__(self, master, on_update, on_elev_preview, *args, **kwargs):
        super().__init__(master, "Elevation Detector", *args, **kwargs)
        grid = self.get_grid()

        self.draw_points_checkbox = Checkbox(
            grid,
            text="Draw Points",
            command=on_update,
            saving_id="elevation_draw_points_checkbox",
            default=True,
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ne")

        self.draw_processed_checkbox = Checkbox(
            grid,
            text="Draw Processed",
            command=on_update,
            saving_id="elevation_draw_processed_checkbox",
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ne")

        self.fov_slider = Slider(
            grid, "FOV", "elevation_fov_slider", 80, 103, 103, on_update, False
        )
        self.fov_slider.grid(row=1, column=0, padx=5, pady=5, sticky="ne", columnspan=2)

        self.debug_load_elevation_preview_button = ct.CTkButton(
            grid, text="Load Elev. Preview", command=on_elev_preview
        )
        self.debug_load_elevation_preview_button.grid(row=2, columnspan=2)
