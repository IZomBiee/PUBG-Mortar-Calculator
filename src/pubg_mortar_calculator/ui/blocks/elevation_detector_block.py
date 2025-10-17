import customtkinter as ct
from pubg_mortar_calculator.ui.widgets import *
from .titled_block import TitledBlock

class ElevationDetectorBlock(TitledBlock):
    def __init__(self, master, on_update, on_image_load,*args, **kwargs):
        super().__init__(master, "Elevation Detector", *args, **kwargs)
        grid = self.get_grid()

        self.draw_points_checkbox = Checkbox(
            grid, text="Draw Points",
            command=on_update,
            saving_id='elevation_draw_points_checkbox',
            default=True
            ).grid(row=0, column=0, padx=5, pady=5, sticky="ne")

        self.draw_processed_checkbox = Checkbox(
            grid, text="Draw Processed",
            command=on_update,
            saving_id='elevation_draw_processed_checkbox'
            ).grid(row=0, column=1, padx=5, pady=5, sticky="ne")
        
        self.load_example_button = ct.CTkButton(
            grid, text='Load Elevation Image',
            command=on_image_load)
        self.load_example_button.grid(row=1, column=0,
            columnspan=2, padx=5, pady=5, sticky="nwse")