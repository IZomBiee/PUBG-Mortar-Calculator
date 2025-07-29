import cv2
import threading
import os
import numpy as np
import datetime
import time
import onnxruntime as ort

from tkinter import messagebox, simpledialog
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .app import App

from .utils import *
from .settings_loader import SettingsLoader as SL
from .grid_detector import GridDetector
from .mark_detector import MarkDetector
from .sample_loader import SampleLoader
from .height_detector import HeightDetector

class AppLogic():
    def __init__(self):
        self.app_ui: App | None = None
    
    def on_ui_load(self):
        self.grid_detector = GridDetector()
        self.mark_detector = MarkDetector()
        self.sample_loader = SampleLoader()

        self.last_image: np.ndarray | None = None
        path = SL().get('Last Preview Path')
        if path is not None and isinstance(path, str):
            self.load_preview_image(path)

    def load_preview_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = get_image_path()
            if path == '':
                return None
            else:
                self.last_image = cv2.imread(path)
                self.reload_preview_image()
                SL().set('Last Preview Path', path)
                return self.last_image
        else:
            if os.path.exists(path):
                self.last_image = cv2.imread(path)
                self.reload_preview_image()
                return self.last_image
            else:
                return None
    
    def reload_preview_image(self, combat_mode:bool = False):
        if combat_mode:
            self.last_image = take_screenshot()

        if self.last_image is None:
            print("No image loaded!")
            return
        elif self.app_ui is None: 
            print("No App UI loaded!")
            return

        draw_frame = self.last_image.copy()

        canny_frame = self.grid_detector.get_canny_frame(draw_frame,
                            self.app_ui.grid_detection_canny1_threshold_slider.get(),
                            self.app_ui.grid_detection_canny2_threshold_slider.get())
        self.grid_detector.detect_lines(canny_frame,
                                        self.app_ui.grid_detection_line_threshold_slider.get(),
                                        self.app_ui.grid_detection_line_gap_slider.get())
        grid_gap = self.grid_detector.get_grid_gap(
            self.app_ui.grid_detection_gap_threshold_slider.get())

        hsv_mask = self.mark_detector.get_hsv_mask(draw_frame,
                                                   self.app_ui.mark_color_combobox.get())
        player_pos, mark_pos = self.mark_detector.get_mark_positions(hsv_mask,
            self.app_ui.mark_max_radius_slider.get())

        if player_pos is not None and \
        mark_pos is not None and grid_gap is not None:
            distance = round(self.grid_detector.get_distance(
                player_pos, mark_pos, grid_gap))
        else: distance = 0

        if combat_mode:
            if self.app_ui.general_settings_dictor_checkbox.get():
                text_to_speech(f"Range {distance}")

            if self.app_ui.elevation_enable_checkbox.get():
                raise NotImplementedError("In development")
                self.app_ui.calculation_elevation_label.configure(text='Disabled')
                game_hsv_mask = self.mark_detector.get_hsv_mask(take_screenshot(),
                                self.app_ui.mark_color_combobox.get())
                game_hsv_mask = game_hsv_mask[300:, :]
                cx, cy = HeightDetector.get_center_point(game_hsv_mask)
                game_hsv_mask = HeightDetector.cut_x_line(game_hsv_mask, cx)
                game_mark_pos = self.mark_detector.get_mark_positions(game_hsv_mask, 100)[0]
                if game_mark_pos is None:
                    text_to_speech("No mark founded")
                else:
                    text_to_speech(f"Found mark")
                    elevation = HeightDetector.get_elevation(cy, game_mark_pos[1], 90, distance)
                    corrected_distance = HeightDetector.get_correct_distance(elevation, distance)
                    text_to_speech(f"Correct Distance {round(corrected_distance)}")
                    print(f"Was {distance}, become {corrected_distance}")
            else:
                self.app_ui.calculation_elevation_label.configure(text='Disabled')

            if self.app_ui.general_settings_add_to_test_samples_checkbox.get():
                self.sample_loader.add(player_pos, mark_pos, grid_gap,
                                       self.app_ui.mark_color_combobox.get(),
                                       draw_frame)

        if self.app_ui.grid_detection_show_processed_image_checkbox.get():
            draw_frame = cv2.cvtColor(canny_frame, cv2.COLOR_GRAY2BGR)

        elif self.app_ui.mark_show_processed_image_checkbox.get():
            draw_frame = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.grid_detection_draw_grid_lines_checkbox.get():
            self.grid_detector.draw_lines(draw_frame)

        if self.app_ui.mark_draw_checkbox.get():
            if player_pos is not None:
                self.mark_detector.draw_mark(draw_frame, player_pos, "Player", (255, 0, 0))
            if mark_pos is not None:
                self.mark_detector.draw_mark(draw_frame, mark_pos, "Mark", (0, 0, 255))

        if mark_pos is not None and player_pos is not None \
        and self.app_ui.mark_zoom_to_points_checkbox.get():
            draw_frame = HeightDetector.cut_to_points(draw_frame, mark_pos, player_pos)

        self.app_ui.preview_image.set_cv2(draw_frame)

        self._set_calculation_data(grid_gap, player_pos,
                                    mark_pos, distance)
    
    def _set_calculation_data(self, grid_gap:int|None,
                               player_pos:tuple[int, int]|None,
                               mark_pos:tuple[int, int]|None,
                               distance:float|None):
        if self.app_ui is None: 
            print("No App UI loaded!")
            return
        
        self.app_ui.calculation_grid_gap_label.configure(text=f'{grid_gap}')
        self.app_ui.calculation_mark_cordinates_label.configure(text=f'{mark_pos}')
        self.app_ui.calculation_player_cordinates_label.configure(text=f'{player_pos}')
        self.app_ui.calculation_distance_label.configure(text=f'{distance}')