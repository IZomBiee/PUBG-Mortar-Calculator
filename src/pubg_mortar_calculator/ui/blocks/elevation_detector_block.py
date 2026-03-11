import customtkinter as ct

from src.customtkinter_widgets import Checkbox, Slider


class ElevationDetectorBlock(ct.CTkFrame):
    def __init__(self, master, on_update, on_elev_preview, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.grid_columnconfigure([0, 1], weight=1)
        self.grid_rowconfigure([0, 1, 2, 3, 4, 5], weight=1)

        self.draw_points_checkbox = Checkbox(
            self,
            text="Draw Points",
            command=on_update,
            saving_id="elevation_draw_points_checkbox",
            default=True,
        ).grid(row=0, column=0, padx=5, pady=5)

        self.draw_processed_checkbox = Checkbox(
            self,
            text="Draw Processed",
            command=on_update,
            saving_id="elevation_draw_processed_checkbox",
        ).grid(row=0, column=1, padx=5, pady=5)

        self.fov_slider = Slider(
            self, "FOV", "elevation_fov_slider", 80, 103, 103, on_update, False
        )
        self.fov_slider.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
        )

        self.debug_load_elevation_preview_button = ct.CTkButton(
            self, text="Load Elev. Preview", command=on_elev_preview
        )
        self.debug_load_elevation_preview_button.grid(row=2, column=0, columnspan=2)
