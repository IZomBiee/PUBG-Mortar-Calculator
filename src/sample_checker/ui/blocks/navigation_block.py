import customtkinter as ct
from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class NavigationBlock(TitledBlock):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, "Navigation", *args, **kwargs)
        grid = self.get_grid()

        self.left_button = ct.CTkButton(grid, text="Left")
        self.left_button.grid(row=0, column=0)
        self.image_number_label = ct.CTkLabel(grid, text="Page: 0/0")
        self.image_number_label.grid(row=0, column=1)
        self.right_button = ct.CTkButton(grid, text="Right")
        self.right_button.grid(row=0, column=2)