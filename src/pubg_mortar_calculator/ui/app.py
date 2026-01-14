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
            (500, 290),
            save_aspect_ratio=True).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.elevation_image = Image(self.left_frame,
            (60, 450), save_aspect_ratio=True
            ).grid(row=0, column=3, rowspan=2, padx=5, pady=5)
        
        self.map_data_block = CalculationDataBlock(
            self.left_frame, "Map Data",
            ['Grid Gap', 'Mark Pos', 'Player Pos', 'Distance'])
        self.map_data_block.grid(row=1, column=0)

        self.elevation_data_block = CalculationDataBlock(
            self.left_frame, "Elevation Data",
            ['Mark Pos', 'Elevation', 'Elevated Distance', 'Mortar Elev. Dist.'])
        self.elevation_data_block.grid(row=1, column=1)

        # Center Frame
        self.center_frame = ct.CTkFrame(self, fg_color='transparent')
        self.center_frame.grid(row=0, column=1)

        self.grid_detector_block = GridDetectorBlock(
            self.center_frame, self.process_map_image)
        self.grid_detector_block.grid(row=0, column=0)

        self.map_detector_block = MapDetectorBlock(
            self.center_frame,  self.process_map_image, self.load_map_image
        )
        self.map_detector_block.grid(row=1, column=0)
        
        # Right Frame
        self.right_frame = ct.CTkFrame(self, fg_color='transparent')
        self.right_frame.grid(row=0, column=2)

        self.dictor_settings_block = DictorSettingsBlock(
            self.right_frame)
        self.dictor_settings_block.grid(row=0, column=0)

        self.general_settings_block = GeneralSettingsBlock(
            self.right_frame
        )
        self.general_settings_block.grid(row=1, column=0)

        self.elevation_detector_block = ElevationDetectorBlock(
            self.right_frame, self.process_elevation_image,
            self.load_elevation_image)
        self.elevation_detector_block.grid(row=2, column=0)
        self.app_ui = self
        AppLogic.__init__(self, self.app_ui)

    def get_calculation_key(self) -> str:
        return self.general_settings_block.map_hotkey_entry.get()
    
    def get_elevation_key(self) -> str:
        return self.general_settings_block.elevation_hotkey_entry.get()
        
    def get_all_in_one_key(self) -> str:
        return self.general_settings_block.all_in_one_hotkey_entry.get()