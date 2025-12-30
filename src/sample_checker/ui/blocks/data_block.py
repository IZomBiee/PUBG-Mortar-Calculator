import customtkinter as ct
from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class DataBlock(TitledBlock):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, "Data", *args, **kwargs)
        grid = self.get_grid()
        
        self.grid_gap_slider = Slider(grid, "Grid Gap").grid(row=0)

        self.player_mark_x_slider = Slider(grid, "Player Mark X").grid(row=1)
        self.player_mark_y_slider = Slider(grid, "Player Mark Y").grid(row=2)

        self.mark_x_slider = Slider(grid, "Mark X").grid(row=3)
        self.mark_y_slider = Slider(grid, "Mark Y").grid(row=4)

        self.elevation_mark_x_slider = Slider(grid, "Elevation Mark X").grid(row=5)
        self.elevation_mark_y_slider = Slider(grid, "Elevation Mark Y").grid(row=6)