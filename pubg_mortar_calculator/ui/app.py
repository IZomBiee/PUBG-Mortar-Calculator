import time
import tkinter

import customtkinter as ct

from pubg_mortar_calculator.core.app_logic import AppLogic
from pubg_mortar_calculator.core.app_overlay import *
from pubg_mortar_calculator.core.hotkey_service import HotkeyService
from pubg_mortar_calculator.core.models import (
    DictorSettings,
    ElevationSettings,
    GeneralSettings,
    GridSettings,
    MarkSettings,
    MinimapSettings,
    OverlaySettings,
)
from pubg_mortar_calculator.customtkinter_widgets import Image
from pubg_mortar_calculator.logger import get_logger
from pubg_mortar_calculator.ui.blocks import (
    CalculationDataBlock,
    DictorSettingsBlock,
    ElevationDetectorBlock,
    GeneralSettingsBlock,
    GridDetectorBlock,
    MarkDetectorBlock,
    MinimapDetectorBlock,
    OverlaySettingsBlock,
)
from pubg_mortar_calculator.utils import paths, take_screenshot

LOGGER = get_logger()


class App(ct.CTk):
    def __init__(self):
        super().__init__()
        self.title("PUBG-Mortar-Calculator")

        self.iconbitmap(paths.icon())
        self.resizable(False, False)

        self.logic = AppLogic()

        # Left Frame
        self.left_frame = ct.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5)

        self.map_image_preview = Image(
            self.left_frame, (500, 290), save_aspect_ratio=True
        )
        self.map_image_preview.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.elevation_image_preview = Image(
            self.left_frame, (60, 450), save_aspect_ratio=True
        )
        self.elevation_image_preview.grid(row=0, column=3, rowspan=2, padx=5, pady=5)

        self.map_data_block = CalculationDataBlock(
            self.left_frame,
            "Map Data",
            ["Grid Gap", "Mark Pos", "Player Pos", "Distance", "Minimap"],
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
        self.tabview.add("Mark")
        self.tabview.add("Elevation")
        self.tabview.add("Minimap")
        self.tabview.add("Dictor")
        self.tabview.add("Overlay")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.general_settings_block = GeneralSettingsBlock(
            self.tabview.tab("General"),
            self._initialize_overlay,
            self._update_all_hotkeys,
        )
        self.general_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.dictor_settings_block = DictorSettingsBlock(self.tabview.tab("Dictor"))
        self.dictor_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.elevation_detector_block = ElevationDetectorBlock(
            self.tabview.tab("Elevation"),
            self.process_elevation_image,
            self.load_elevation_preview,
        )
        self.elevation_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.minimap_detector_block = MinimapDetectorBlock(
            self.tabview.tab("Minimap"), self.process_map_image
        )
        self.minimap_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.grid_detector_block = GridDetectorBlock(
            self.tabview.tab("Grid"), self.process_map_image
        )
        self.grid_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.mark_detector_block = MarkDetectorBlock(
            self.tabview.tab("Mark"), self.process_map_image, self.load_map_preview
        )
        self.mark_detector_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.overlay_settings_block = OverlaySettingsBlock(
            self.tabview.tab("Overlay"), self._initialize_overlay
        )
        self.overlay_settings_block.pack(fill="both", expand=True, padx=5, pady=5)

        self.overlay: None | AppOverlay = None

        self._load_initial_previews()
        self._initialize_overlay()

        self.hotkey_service = HotkeyService()
        self._update_all_hotkeys()

        if not paths.map_detection_model().exists():
            LOGGER.warning(
                "Can't find minimap detection model at "
                + paths.map_detection_model().as_posix()
            )
            self.minimap_detector_block.enabled_checkbox.checkbox.configure(
                state=tkinter.DISABLED
            )
            self.minimap_detector_block.enabled_checkbox.set(False)

        if not paths.mark_detection_model().exists():
            LOGGER.warning(
                "Can't find mark detection model at "
                + paths.mark_detection_model().as_posix()
            )
            self.mark_detector_block.yolo_checkbox.checkbox.configure(
                state=tkinter.DISABLED
            )
            self.mark_detector_block.yolo_checkbox.set(False)

    def _load_initial_previews(self):
        if self.logic.map_image is not None:
            self.process_map_image(combat=False)

    def _update_all_hotkeys(self):
        settings = self._get_general_settings()
        self.update_map_hotkey(settings.calculation_hotkey)
        self.update_elevation_hotkey(settings.elevation_hotkey)
        self.update_all_in_one_hotkey(settings.all_in_one_hotkey)

    def process_map_image(self, combat: bool = False, dictor: bool = True):
        if combat:
            if self.overlay is not None:
                self.overlay.add_command(Clear())
                time.sleep(0.05)
            self.logic.map_image = take_screenshot(
                self._get_general_settings().monitor_id
            )

        if self.logic.map_image is None:
            return

        dictor_settings = self._get_dictor_settings()
        dictor_settings.enabled = dictor_settings.enabled and dictor

        processed_img, map_data = self.logic.set_map_image(
            self.logic.map_image,
            grid_settings=self._get_grid_settings(),
            mark_settings=self._get_mark_settings(),
            minimap_settings=self._get_minimap_settings(),
            dictor_settings=dictor_settings,
            general_settings=self._get_general_settings(),
            combat=combat,
        )

        self.map_image_preview.set_cv2(processed_img)
        self._update_map_data_ui(map_data)

        self.process_elevation_image(False)

        if self.overlay is not None:
            self.logic.draw_to_overlay(self.overlay, self._get_overlay_settings())

    def update_map_hotkey(self, key_str: str):
        self.hotkey_service.bind(
            action_name="map_calculation",
            key_combo=key_str,
            callback=lambda: self.after(0, lambda: self.process_map_image(True)),
        )

    def update_elevation_hotkey(self, key_str: str):
        self.hotkey_service.bind(
            action_name="elevation_calculation",
            key_combo=key_str,
            callback=lambda: self.after(0, lambda: self.process_elevation_image(True)),
        )

    def update_all_in_one_hotkey(self, key_str: str):
        self.hotkey_service.bind(
            action_name="all_in_one_calculation",
            key_combo=key_str,
            callback=lambda: self.after(0, self.all_in_one_calculation),
        )

    def process_elevation_image(self, combat: bool = False):
        if combat:
            if self.overlay is not None:
                self.overlay.add_command(Clear())
                time.sleep(0.05)
            self.logic.elevation_image = take_screenshot(
                self._get_general_settings().monitor_id
            )

        if self.logic.elevation_image is None:
            return

        processed_img, elev_data = self.logic.set_elevation_image(
            self.logic.elevation_image,
            elevation_settings=self._get_elevation_settings(),
            mark_settings=self._get_mark_settings(),
            dictor_settings=self._get_dictor_settings(),
            general_settings=self._get_general_settings(),
            combat=combat,
        )

        if self.overlay is not None and combat:
            self.logic.draw_to_overlay(self.overlay, self._get_overlay_settings())

        self.elevation_image_preview.set_cv2(processed_img)
        self._update_elevation_data_ui(elev_data)

    def all_in_one_calculation(self):
        self.process_map_image(True, False)
        self.process_elevation_image(True)

    def _get_grid_settings(self) -> GridSettings:
        return GridSettings(
            canny1=self.grid_detector_block.canny1_threshold_slider.get(),
            canny2=self.grid_detector_block.canny2_threshold_slider.get(),
            line_threshold=self.grid_detector_block.line_threshold_slider.get() / 100,
            line_gap=self.grid_detector_block.line_gap_slider.get() / 100,
            line_merge=self.grid_detector_block.line_merge_threshold_slider.get(),
            show_processed=self.grid_detector_block.show_processed_image_checkbox.get(),
            draw_lines=self.grid_detector_block.draw_grid_lines_checkbox.get(),
        )

    def _get_mark_settings(self) -> MarkSettings:
        return MarkSettings(
            use_yolo=self.mark_detector_block.yolo_checkbox.get(),
            color=self.mark_detector_block.color_combobox.get(),
            min_radius=self.mark_detector_block.min_radius_slider.get(),
            max_radius=self.mark_detector_block.max_radius_slider.get(),
            draw_marks=self.mark_detector_block.draw_checkbox.get(),
            zoom_to_points=self.mark_detector_block.zoom_to_points_checkbox.get(),
            show_processed=self.mark_detector_block.show_processed_image_checkbox.get(),
        )

    def _get_minimap_settings(self) -> MinimapSettings:
        return MinimapSettings(
            enabled=self.minimap_detector_block.enabled_checkbox.get(),
            offset=self.minimap_detector_block.offset_slider.get(),
            small_size=self.minimap_detector_block.small_minimap_size_slider.get(),
            large_size=self.minimap_detector_block.large_minimap_size_slider.get(),
        )

    def _get_elevation_settings(self) -> ElevationSettings:
        return ElevationSettings(
            fov=self.elevation_detector_block.fov_slider.get(),
            draw_processed=self.elevation_detector_block.draw_processed_checkbox.get(),
            draw_points=self.elevation_detector_block.draw_points_checkbox.get(),
        )

    def _get_dictor_settings(self) -> DictorSettings:
        return DictorSettings(
            enabled=self.dictor_settings_block.dictor_checkbox.get(),
            volume=self.dictor_settings_block.volume_slider.get(),
            rate=self.dictor_settings_block.rate_slider.get(),
        )

    def _get_general_settings(self) -> GeneralSettings:
        try:
            monitor_id = int(self.general_settings_block.monitor_id_entry.get())
        except ValueError:
            monitor_id = 0

        return GeneralSettings(
            debug_mode=self.general_settings_block.debug_mode_checkbox.get(),
            calculation_hotkey=self.general_settings_block.map_hotkey_entry.get(),
            elevation_hotkey=self.general_settings_block.elevation_hotkey_entry.get(),
            all_in_one_hotkey=self.general_settings_block.all_in_one_hotkey_entry.get(),
            app_title=self.general_settings_block.title_entry.get(),
            monitor_id=monitor_id,
        )

    def _get_overlay_settings(self) -> OverlaySettings:
        return OverlaySettings(
            enabled=self.overlay_settings_block.enabled_checkbox.get(),
            draw_borders=self.overlay_settings_block.draw_borders_checkbox.get(),
            scale=self.overlay_settings_block.scale_slider.get(),
            draw_map_marks=self.overlay_settings_block.draw_map_marks_checkbox.get(),
            draw_elevation_marks=self.overlay_settings_block.draw_elevation_marks_checkbox.get(),
            draw_minimap=self.overlay_settings_block.draw_minimap_box_checkbox.get(),
        )

    def _update_map_data_ui(self, data):
        self.map_data_block.set_value(
            "Grid Gap", f"{data.grid_gap}px" if data.grid_gap else "None"
        )
        self.map_data_block.set_value("Mark Pos", str(data.mark_position))
        self.map_data_block.set_value("Player Pos", str(data.player_position))
        self.map_data_block.set_value(
            "Distance", f"{round(data.distance, 1)}m" if data.distance else "None"
        )
        minimap_types = ["No", "Small", "Large"]
        self.map_data_block.set_value("Minimap", minimap_types[data.minimap_type.value])

    def _update_elevation_data_ui(self, data):
        self.elevation_data_block.set_value("Mark Pos", str(data.mark_position))
        self.elevation_data_block.set_value(
            "Elevation",
            f"{round(data.elevation, 1)}m" if data.elevation is not None else "None",
        )
        self.elevation_data_block.set_value(
            "Elevated Distance",
            f"{round(data.elevated_distance, 1)}m"
            if data.elevated_distance is not None
            else "None",
        )
        dist_str = (
            f"{data.mortar_elevated_distance} m"
            if isinstance(data.mortar_elevated_distance, int)
            else str(data.mortar_elevated_distance)
        )
        self.elevation_data_block.set_value("Mortar Elev. Dist.", dist_str)

    def _initialize_overlay(self):
        if self.overlay is not None:
            self.overlay.stop()

        settings = self._get_overlay_settings()
        if settings.enabled:
            self.overlay = AppOverlay(self._get_general_settings().app_title)
            self.logic.draw_to_overlay(self.overlay, self._get_overlay_settings())

    def load_map_preview(self):
        image = self.logic.load_image()
        if image is None:
            return

        processed_image, map_data = self.logic.set_map_image(
            image,
            self._get_grid_settings(),
            self._get_mark_settings(),
            self._get_minimap_settings(),
            self._get_dictor_settings(),
            self._get_general_settings(),
            False,
        )
        self.map_image_preview.set_cv2(processed_image)
        self._update_map_data_ui(map_data)
        self.process_elevation_image(False)

    def load_elevation_preview(self):
        image = self.logic.load_image()
        if image is None:
            return

        self.logic.set_elevation_image(
            image,
            self._get_elevation_settings(),
            self._get_mark_settings(),
            self._get_dictor_settings(),
            self._get_general_settings(),
            False,
        )

        processed_image, elevation_data = self.logic.set_elevation_image(
            image,
            self._get_elevation_settings(),
            self._get_mark_settings(),
            self._get_dictor_settings(),
            self._get_general_settings(),
            False,
        )
        self.elevation_image_preview.set_cv2(processed_image)
        self._update_elevation_data_ui(elevation_data)
