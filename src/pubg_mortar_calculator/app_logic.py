import os
import shutil
import tkinter
from typing import TYPE_CHECKING

import cv2
import numpy as np
import pygetwindow

if TYPE_CHECKING:
    from .ui.app import App

from dataclasses import dataclass
from datetime import datetime

from src import app_overlay
from src.app_overlay import *

from .detectors import GridDetector, MapDetector, MarkDetector
from .dictor_manager import DictorManager
from .elevation_tools import ElevationTools
from .logger import get_logger
from .utils import imgpr, paths

LOGGER = get_logger()


@dataclass
class MapData:
    distance: float | None = None
    grid_gap: int | None = None
    player_position: tuple[int, int] | None = None
    mark_position: tuple[int, int] | None = None
    box: list[int] | None = None


@dataclass
class ElevationData:
    elevation: float | None = None
    mark_position: tuple[int, int] | None = None
    center_position: tuple[int, int] | None = None
    elevated_distance: float | None = None
    mortar_elevated_distance: int | str | None = None


class AppLogic:
    def __init__(self, app_ui: "App"):
        self.app_ui: "App" = app_ui

        self.map_image: np.ndarray | None = None
        self.map_data = MapData()

        self.elevation_image: np.ndarray | None = None
        self.elevation_data = ElevationData()

        with open(paths.mortar_distances(), "r") as file:
            self.mortar_distances = [int(i) for i in file.readlines()]

        self.grid_detector = GridDetector()
        self.mark_detector = MarkDetector()

        self.overlay = None

        self._load_map_detector()

        self.dictor_manager = DictorManager(
            self.app_ui.dictor_settings_block.rate_slider.get(),
            self.app_ui.dictor_settings_block.volume_slider.get() / 100,
        )
        self.dictor_manager.start()

        self._load_saved_images()

        self.process_map_image(False)
        self.process_elevation_image(False)

        self._initialize_overlay()

    def process_map_image(self, combat: bool = False):
        if self.map_image is None:
            return

        processed_image = self.map_image.copy()

        if (
            self.app_ui.map_detector_block.minimap_detection.get()
            and self.map_detector is not None
        ):
            self.map_data.box = self.map_detector.detect(processed_image)
            if self.map_data.box is not None:
                x0, y0, x1, y1 = self.map_data.box
                processed_image = imgpr.cut_to_points(
                    processed_image, (x0, y0), (x1, y1), 0
                )[0]
        else:
            self.map_data.box = None

        canny_image = self.grid_detector.get_canny_frame(
            processed_image,
            self.app_ui.grid_detector_block.canny1_threshold_slider.get(),
            self.app_ui.grid_detector_block.canny2_threshold_slider.get(),
        )

        lines = self.grid_detector.get_normalized_lines(
            canny_image,
            self.app_ui.grid_detector_block.line_threshold_slider.get() / 100,
            self.app_ui.grid_detector_block.line_gap_slider.get() / 100,
            self.app_ui.grid_detector_block.line_merge_threshold_slider.get(),
        )

        self.map_data.grid_gap = self.grid_detector.calculate_grid_gap(*lines)

        if self.map_data.box is None:
            self.mark_detector.remove_danger_zones(processed_image)

        hsv_mask = self.mark_detector.get_hsv_mask(
            processed_image, self.app_ui.map_detector_block.color_combobox.get()
        )

        self.map_data.player_position, self.map_data.mark_position = (
            self.mark_detector.get_mark_positions(
                hsv_mask, self.app_ui.map_detector_block.max_radius_slider.get()
            )
        )

        if (
            self.map_data.player_position is not None
            and self.map_data.mark_position is not None
            and self.map_data.grid_gap is not None
        ):
            self.map_data.distance = self.grid_detector.get_distance(
                self.map_data.player_position,
                self.map_data.mark_position,
                self.map_data.grid_gap,
            )
        else:
            self.map_data.distance = None

        if self.app_ui.grid_detector_block.show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2BGR)

        elif self.app_ui.map_detector_block.show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)

        if self.app_ui.grid_detector_block.draw_grid_lines_checkbox.get():
            self.grid_detector.draw_lines(processed_image, *lines)

        if self.app_ui.map_detector_block.draw_checkbox.get():
            self.mark_detector.draw_marks(
                processed_image,
                self.map_data.player_position,
                self.map_data.mark_position,
            )

        if (
            self.map_data.mark_position is not None
            and self.map_data.player_position is not None
            and self.app_ui.map_detector_block.zoom_to_points_checkbox.get()
        ):
            processed_image = imgpr.cut_to_points(
                processed_image,
                self.map_data.mark_position,
                self.map_data.player_position,
            )[0]

        LOGGER.info(
            f"Map calculation [Distance: {self.map_data.distance} Grid gap: {self.map_data.grid_gap}"
            + f" Player pos: {self.map_data.mark_position} Mark pos: {self.map_data.player_position}]"
            + f" Combat: {combat}"
        )

        if self.app_ui.dictor_settings_block.dictor_checkbox.get() and combat:
            self.dictor_manager.add(self.map_data.distance)

        self._calculate_elevation_data()
        self._update_elevation_data()

        self._draw_data_in_overlay()

        self.app_ui.map_image_preview.set_cv2(processed_image)
        self._update_map_data()

    def process_elevation_image(self, combat: bool = False):
        if self.elevation_image is None:
            return

        processed_image = self.elevation_image.copy()

        cut_y = int(processed_image.shape[0] * 0.2)
        imgpr.replace_area_with_black(
            processed_image, (0, 0), (processed_image.shape[1], cut_y)
        )

        self.elevation_data.center_position = imgpr.get_center_point(processed_image)
        processed_image, (x0, _) = imgpr.cut_x_line(
            processed_image, self.elevation_data.center_position[0], 0.02
        )
        cutted_center = imgpr.get_center_point(processed_image)

        hsv_mask_image = self.mark_detector.get_hsv_mask(
            processed_image, self.app_ui.map_detector_block.color_combobox.get()
        )

        self.elevation_data.mark_position = self.mark_detector.get_mark_positions(
            hsv_mask_image, self.app_ui.map_detector_block.max_radius_slider.get()
        )[0]

        self._calculate_elevation_data()

        if self.app_ui.elevation_detector_block.draw_processed_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask_image, cv2.COLOR_GRAY2BGR)

        self._draw_data_in_overlay()

        if self.app_ui.elevation_detector_block.draw_points_checkbox.get():
            cv2.circle(processed_image, cutted_center, 2, (0, 255, 0), 5)
            if self.elevation_data.mark_position is not None:
                cv2.arrowedLine(
                    processed_image,
                    cutted_center,
                    self.elevation_data.mark_position,
                    (0, 255, 0),
                    3,
                )
                cv2.circle(
                    processed_image,
                    self.elevation_data.mark_position,
                    2,
                    (0, 255, 0),
                    5,
                )

        self._update_elevation_data()

        LOGGER.info(
            f"Elevation calculation [Mortar Distance: {self.elevation_data.mortar_elevated_distance}"
            + f" Elevated Distance: {self.elevation_data.mortar_elevated_distance}"
            + f" Elevation: {self.elevation_data.elevation} Mark pos: {self.elevation_data.mark_position}]"
            + f" Combat: {combat}"
        )

        if self.app_ui.dictor_settings_block.dictor_checkbox.get() and combat:
            self.dictor_manager.add(self.elevation_data.mortar_elevated_distance)

        self.app_ui.elevation_image_preview.set_cv2(
            processed_image[cut_y : processed_image.shape[0]]
        )

    def set_map_image(self, image: np.ndarray, combat: bool = True):
        self.map_image = image
        self.process_map_image(combat)
        self._save_map_image()

    def set_elevation_image(self, image: np.ndarray, combat: bool = True):
        self.elevation_image = image
        self.process_elevation_image(combat)
        self._save_elevation_image()

    def _calculate_elevation_data(self):
        if self.elevation_data.mark_position is None or self.map_data.distance is None:
            self.elevation_data.elevation = None
        elif (
            self.elevation_data.center_position is not None
            and self.map_data.distance is not None
        ):
            self.elevation_data.elevation = ElevationTools.get_elevation(
                self.elevation_data.center_position[1],
                self.elevation_data.mark_position[1],
                self.app_ui.elevation_detector_block.fov_slider.get(),
                self.map_data.distance,
            )

        if (
            self.elevation_data.elevation is not None
            and self.map_data.distance is not None
        ):
            self.elevation_data.elevated_distance = (
                ElevationTools.get_elevated_distance(
                    self.map_data.distance, self.elevation_data.elevation
                )
            )
            if self.elevation_data.elevated_distance == 0:
                self.elevation_data.elevated_distance = None
        else:
            self.elevation_data.elevated_distance = None

        if self.elevation_data.elevated_distance is None:
            self.elevation_data.mortar_elevated_distance = None
        elif self.elevation_data.elevated_distance < 120:
            self.elevation_data.mortar_elevated_distance = "Too close"
        elif self.elevation_data.elevated_distance > 705:
            self.elevation_data.mortar_elevated_distance = "Too far"
        else:
            self.elevation_data.mortar_elevated_distance = (
                ElevationTools.calculate_mortar_distance(
                    self.elevation_data.elevated_distance, self.mortar_distances
                )
            )

    def _save_map_image(self):
        if self.map_image is None:
            return
        cv2.imwrite(paths.map_preview(), self.map_image)
        if self.app_ui.general_settings_block.debug_mode_checkbox.get():
            saving_path = f"{paths.debug_files()}\\{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_map')}.png"
            LOGGER.info(f"Map preview was saved in {saving_path}")
            shutil.copy2(paths.map_preview(), saving_path)

    def _save_elevation_image(self):
        if self.elevation_image is None:
            return
        cv2.imwrite(paths.elevation_preview(), self.elevation_image)
        if self.app_ui.general_settings_block.debug_mode_checkbox.get():
            saving_path = f"{paths.debug_files()}\\{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_elevation')}.png"
            LOGGER.info(f"Elevation preview was saved in {saving_path}")
            shutil.copy2(paths.elevation_preview(), saving_path)

    def _update_elevation_data(self):
        self.app_ui.elevation_data_block.set_value(
            "Mark Pos", str(self.elevation_data.mark_position)
        )

        if self.elevation_data.elevation is not None:
            self.app_ui.elevation_data_block.set_value(
                "Elevation", str(round(self.elevation_data.elevation, 1)) + "m"
            )
        else:
            self.app_ui.elevation_data_block.set_value("Elevation", "None")

        if self.elevation_data.elevated_distance is not None:
            self.app_ui.elevation_data_block.set_value(
                "Elevated Distance",
                str(round(self.elevation_data.elevated_distance, 1)) + "m",
            )
        else:
            self.app_ui.elevation_data_block.set_value("Elevated Distance", "None")

        if isinstance(self.elevation_data.mortar_elevated_distance, int):
            self.app_ui.elevation_data_block.set_value(
                "Mortar Elev. Dist.",
                f"{self.elevation_data.mortar_elevated_distance} m",
            )
        else:
            self.app_ui.elevation_data_block.set_value(
                "Mortar Elev. Dist.",
                str(self.elevation_data.mortar_elevated_distance),
            )

    def _update_map_data(self):
        if self.map_data.grid_gap is not None:
            self.app_ui.map_data_block.set_value(
                "Grid Gap", str(self.map_data.grid_gap) + "px"
            )
        else:
            self.app_ui.map_data_block.set_value("Grid Gap", "None")

        self.app_ui.map_data_block.set_value(
            "Mark Pos", str(self.map_data.mark_position)
        )
        self.app_ui.map_data_block.set_value(
            "Player Pos", str(self.map_data.player_position)
        )
        if self.map_data.distance is not None:
            self.app_ui.map_data_block.set_value(
                "Distance", str(round(self.map_data.distance, 1)) + "m"
            )
        else:
            self.app_ui.map_data_block.set_value("Distance", "None")

    def _load_saved_images(self):
        if os.path.exists(paths.map_preview()):
            self.map_image = cv2.imread(paths.map_preview())
        if os.path.exists(paths.elevation_preview()):
            self.elevation_image = cv2.imread(paths.elevation_preview())

    def _draw_data_in_overlay(self):
        if self.overlay is None:
            return

        self.overlay.add_command(Clear())

        if self.app_ui.overlay_settings_block.draw_borders_checkbox.get():
            self.overlay.add_command(DrawBorders())

        def fmt(val, precision=".1f"):
            return "None" if val is None else f"{val:{precision}}"

        text_to_display = [
            f"Distance: {fmt(self.map_data.distance)}",
            f"Mortar Distance: {self.elevation_data.mortar_elevated_distance}",
            f"Elevation: {fmt(self.elevation_data.elevation)}",
            f"Grid gap: {self.map_data.grid_gap}",
        ]

        y = 30
        for text in text_to_display:
            self.overlay.add_command(CreateText(text, 20, y, "red", 20))
            y += 30

        if self.map_data.box is not None:
            x0, y0, x1, y1 = self.map_data.box
            scale = self.app_ui.overlay_settings_block.scale_slider.get() / 100

            self.overlay.add_command(
                CreateRect(
                    int(x0 / scale), int(y0 / scale), int(x1 / scale), int(y1 / scale)
                )
            )

    def _initialize_overlay(self):
        if self.app_ui.overlay_settings_block.enabled_checkbox.get():
            if self.overlay is None:
                LOGGER.info("Starting overlay process...")

                self.overlay = app_overlay.AppOverlay("")

            self._draw_data_in_overlay()

            self.overlay.add_command(
                ChangeApp(self.app_ui.overlay_settings_block.title_entry.get())
            )

            windows = pygetwindow.getAllWindows()
            window = None
            for window in windows:
                if (
                    window is not None
                    and self.app_ui.overlay_settings_block.title_entry.get()
                    in window.title
                ):
                    window = window

        elif self.overlay is not None:
            LOGGER.info("Stoping overlay process...")
            self.overlay.add_command(app_overlay.Stop())
            self.overlay = None

    def _load_map_detector(self):
        if os.path.exists(paths.map_detection_model()):
            self.map_detector = MapDetector()
        else:
            LOGGER.warning(
                "Can't find minimap detection model at " + paths.map_detection_model()
            )
            self.map_detector = None
            self.app_ui.map_detector_block.minimap_detection.checkbox.configure(
                state=tkinter.DISABLED
            )
            self.app_ui.map_detector_block.minimap_detection.set(False)
