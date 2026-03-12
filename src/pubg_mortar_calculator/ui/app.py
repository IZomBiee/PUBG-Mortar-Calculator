import customtkinter as ct
import cv2

from src.customtkinter_widgets import Image
from src.pubg_mortar_calculator import utils

from ..app_logic import AppLogic
from .blocks import (
    CalculationDataBlock,
    DictorSettingsBlock,
    ElevationDetectorBlock,
    GeneralSettingsBlock,
    GridDetectorBlock,
    MapDetectorBlock,
    OverlaySettingsBlock,
)


class App(ct.CTk, AppLogic):
    def __init__(self):
        ct.CTk.__init__(self)
        self.title("PUBG-Mortar-Calculator")
        self.resizable(False, False)

        # Left Frame
        self.left_frame = ct.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5)

        self.map_image_preview = Image(
            self.left_frame, (500, 290), save_aspect_ratio=True
        ).grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.elevation_image_preview = Image(
            self.left_frame, (60, 450), save_aspect_ratio=True
        ).grid(row=0, column=3, rowspan=2, padx=5, pady=5)

        self.map_data_block = CalculationDataBlock(
            self.left_frame,
            "Map Data",
            ["Grid Gap", "Mark Pos", "Player Pos", "Distance"],
        )
        self.map_data_block.grid(row=1, column=0)

        self.elevation_data_block = CalculationDataBlock(
            self.left_frame,
            "Elevation Data",
            ["Mark Pos", "Elevation", "Elevated Distance", "Mortar Elev. Dist."],
        )
        self.elevation_data_block.grid(row=1, column=1)

        # Right Frame
        self.right_frame = ct.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1)

        self.tabview = ct.CTkTabview(self.right_frame)
        self.tabview.add("General")
        self.tabview.add("Grid")
        self.tabview.add("Map")
        self.tabview.add("Elevation")
        self.tabview.add("Dictor")
        self.tabview.add("Overlay")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        def on_elev():
            path = utils.paths.get_image()
            if path != "":
                self.set_elevation_image(cv2.imread(path))

        self.general_settings_block = GeneralSettingsBlock(
            self.tabview.tab("General"), self._initialize_overlay
        )
        self.general_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.dictor_settings_block = DictorSettingsBlock(self.tabview.tab("Dictor"))
        self.dictor_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.elevation_detector_block = ElevationDetectorBlock(
            self.tabview.tab("Elevation"), self.process_elevation_image, on_elev
        )
        self.elevation_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.grid_detector_block = GridDetectorBlock(
            self.tabview.tab("Grid"), self.process_map_image
        )
        self.grid_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        def on_map():
            path = utils.paths.get_image()
            if path != "":
                self.set_map_image(cv2.imread(path))

        self.map_detector_block = MapDetectorBlock(
            self.tabview.tab("Map"), self.process_map_image, on_map
        )
        self.map_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.overlay_settings_block = OverlaySettingsBlock(
            self.tabview.tab("Overlay"), self._initialize_overlay
        )
        self.overlay_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.app_ui = self
        AppLogic.__init__(self, self.app_ui)

    def get_calculation_key(self) -> str:
        return self.general_settings_block.map_hotkey_entry.get()

    def get_elevation_key(self) -> str:
        return self.general_settings_block.elevation_hotkey_entry.get()

    def get_all_in_one_key(self) -> str:
        return self.general_settings_block.all_in_one_hotkey_entry.get()
