import cv2
import time
import os
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .app import App
from pubg_mortar_calculator import utils
from .settings_loader import SettingsLoader as SL
from .grid_detector import GridDetector
from .mark_detector import MarkDetector

class AppLogic():
    def __init__(self):
        self.app_ui: App | None = None
    
    def on_ui_load(self):
        self.grid_detector = GridDetector()
        self.mark_detector = MarkDetector()

        self.last_image: np.ndarray | None = None
        path = SL().get('Last Preview Path')
        if path is not None and isinstance(path, str):
            self.load_preview_image(path)

    def load_preview_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = utils.get_image_path()
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
        if self.last_image is None:
            print("No image loaded!")
            return
        elif self.app_ui is None: 
            print("No App UI loaded!")
            return
        
        if combat_mode: self.last_image = utils.take_screenshot()

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
        player_pos, mark_pos = self.mark_detector.get_mark_positions(hsv_mask, 35)

        if player_pos is not None and \
        mark_pos is not None and grid_gap is not None:
            distance = round(self.grid_detector.get_distance(
                player_pos, mark_pos, grid_gap))
        else: distance = 0

        if combat_mode:
            if self.app_ui.general_settings_dictor_checkbox.get():
                utils.text_to_speech(f"Range {distance}")

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

    # def process_preview_image(self, combat_mode=False):
    #     print(f'------------- CALCULATION IN {"COMBAT"if combat_mode else "PREVIEW"} MODE -------------')
    #     if combat_mode:
    #         self.last_image = utils.take_screenshot()
    #         cv2.imwrite(f'screenshots/{time.time()}.png', self.last_image)
    #     else:
    #         if self.last_image is None: return

    #     frame = self.last_image.copy()

    #     grid_detector.detect_lines(frame)
    #     grid_gap = grid_detector.get_grid_gap()
            
    #     self.calculation_grid_gap_label.configure(text=f'{grid_gap}')
    #     print(f"GRID GAP: {grid_gap}")

    #     player_cord, mark_cord = self.mark_detector.get_cords(frame, self.mark_color_combobox.get())
    #     self.calculation_mark_cordinates_label.configure(text=f'{mark_cord}')
    #     self.calculation_player_cordinates_label.configure(text=f'{player_cord}')
    #     print(f'PLAYER POSITION: {player_cord}')
    #     print(f'MARK POSITION: {mark_cord}')

    #     if player_cord is not None and mark_cord is not None and grid_gap is not None:
    #         try:
    #             distance = round(grid_detector.get_distance(player_cord, mark_cord, grid_gap))
    #         except ZeroDivisionError:
    #             distance = 0
            
    #         self.calculation_distance_label.configure(text=f'{distance}')
    #         print(f'DISTANCE: {distance}')

    #         if self.general_settings_add_to_test_samples_checkbox.get() and combat_mode and distance != 0:
    #             self.sample_loader.add(player_cord, mark_cord, grid_gap,
    #                                 self.mark_color_combobox.get(),
    #                                 frame=frame)

    #     if self.grid_detection_show_processed_image_checkbox.get():
    #         frame = cv2.cvtColor(grid_detector.process_frame(frame), cv2.COLOR_GRAY2BGR)
    #         frame = cv2.resize(frame, (int(frame.shape[1]*grid_detector.normalize_multiplier[0]),
    #                                    int(frame.shape[0]*grid_detector.normalize_multiplier[1])))
        
    #     if self.grid_detection_draw_grid_lines_checkbox.get():
    #         grid_detector.draw_lines(frame)
        
    #     if self.mark_draw_checkbox.get():
    #         if player_cord is not None:
    #             self.mark_detector.draw_point(frame, player_cord, "Player", (255, 0, 0))
    #         if mark_cord is not None:
    #             self.mark_detector.draw_point(frame, mark_cord, "Mark", (0, 0, 255))

    #     self.preview_image.set_cv2(frame)
            
    #     if self.general_settings_dictor_checkbox.get() and combat_mode:
    #         utils.text_to_speech(str(distance))
