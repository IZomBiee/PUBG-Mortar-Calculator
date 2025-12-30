import customtkinter as ct

from src.customtkinter_widgets import *
from .blocks import *
from ..app_logic import AppLogic 

class App(ct.CTk, AppLogic):
    def __init__(self):
        ct.CTk.__init__(self)
        self.title("PUBG-Mortar-Calculator")
        self.resizable(False, False)
        self.columnconfigure([0, 1, 2], weight=1)

        # Left Frame
        self.left_frame = ct.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5)

        self.map_image = Image(self.left_frame,
            (384, 216), 
            save_aspect_ratio=True).grid(
            row=0, column=0, padx=5, pady=5)
        
        self.elevation_image = Image(self.left_frame,
            (100, 384), save_aspect_ratio=True
            ).grid(row=0, column=3, rowspan=2, padx=5, pady=5)
        
        self.navigation_block = NavigationBlock(self.left_frame)
        self.navigation_block.grid(row=1, column=0)

        # Right Frame
        self.right_frame = ct.CTkFrame(self, fg_color='transparent')
        self.right_frame.grid(row=0, column=1, padx=5, pady=5)

        self.data_block = DataBlock(self.right_frame)
        self.data_block.grid(row=0, column=0)

        self.app_ui = self
        AppLogic.__init__(self, self.app_ui)