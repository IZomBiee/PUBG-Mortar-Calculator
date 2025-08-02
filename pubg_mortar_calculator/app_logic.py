import cv2
import os
import numpy as np

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
    def __init__(self, app_ui: "App"):
        self.app_ui: "App" = app_ui
        self.last_map_image: np.ndarray | None = None
        self.last_distance = 0

        self.last_elevation_image: np.ndarray|None = None
        self.last_elevation = None

        self.grid_detector = GridDetector()
        self.mark_detector = MarkDetector()
        self.sample_loader = SampleLoader()

        path = SL().get('last_map_image_path')
        if path is not None and isinstance(path, str):
            self.load_map_image(path)

        path = SL().get('last_elevation_image_path')
        if path is not None and isinstance(path, str):
            self.load_elevation_image(path)

    def load_map_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = get_image_path()
            if path == '':
                return None
            else:
                self.last_map_image = cv2.imread(path)
                self.reload_map_image()
                SL().set('last_map_image_path', path)
                return self.last_map_image
        else:
            if os.path.exists(path):
                self.last_map_image = cv2.imread(path)
                self.reload_map_image()
                return self.last_map_image
            else:
                return None
    
    def reload_map_image(self, combat_mode:bool = False):
        if combat_mode:
            self.last_map_image = take_screenshot()

        if self.last_map_image is None:
            print("No image loaded!")
            return
            
        draw_frame = self.last_map_image.copy()

        canny_frame = self.grid_detector.get_canny_frame(draw_frame,
                                    self.app_ui.grid_detection_canny1_threshold_slider.get(),
                                    self.app_ui.grid_detection_canny2_threshold_slider.get())

        self.grid_detector.detect_lines(canny_frame,
                                        self.app_ui.grid_detection_line_threshold_slider.get(),
                                        self.app_ui.grid_detection_line_gap_slider.get())
        
        grid_gap = self.grid_detector.calculate_grid_gap(
            self.app_ui.grid_detection_gap_threshold_slider.get())

        hsv_mask = self.mark_detector.get_hsv_mask(draw_frame,
                                                   self.get_color())
        player_pos, mark_pos = self.mark_detector.get_mark_positions(hsv_mask,
            self.app_ui.mark_max_radius_slider.get())
        
        if player_pos is not None and \
        mark_pos is not None and grid_gap is not None:
            self.last_distance = round(self.grid_detector.get_distance(
                player_pos, mark_pos, grid_gap))
        else: self.last_distance = 0

        if combat_mode:
            if self.is_dictor():
                text_to_speech(f"Range {self.last_distance}")
            else:
                if self.app_ui.general_settings_add_to_test_samples_checkbox.get():
                    self.sample_loader.add(player_pos, mark_pos, grid_gap,
                                        self.get_color(),
                                        draw_frame)

        if self.app_ui.grid_detection_show_processed_image_checkbox.get():
            draw_frame = cv2.cvtColor(canny_frame, cv2.COLOR_GRAY2BGR)

        elif self.app_ui.mark_show_processed_image_checkbox.get():
            draw_frame = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.grid_detection_draw_grid_lines_checkbox.get():
            self.grid_detector.draw_lines(draw_frame)

        if self.app_ui.mark_draw_checkbox.get():
            self.mark_detector.draw_marks(draw_frame)

        if mark_pos is not None and player_pos is not None \
        and self.app_ui.mark_zoom_to_points_checkbox.get():
            draw_frame = HeightDetector.cut_to_points(draw_frame, mark_pos, player_pos)

        self.app_ui.map_image.set_cv2(draw_frame)
        
        self.set_calculation_data(grid_gap=grid_gap, player_pos=player_pos,
                                    mark_pos=mark_pos, distance=self.last_distance)
        
        if self.last_elevation_image is not None:
            self.reload_elevation_image()

    def load_elevation_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = get_image_path()
            if path == '':
                return None
            else:
                self.last_elevation_image = cv2.imread(path)
                self.reload_elevation_image()
                SL().set('last_elevation_image_path', path)
                return self.last_elevation_image
        else:
            if os.path.exists(path):
                self.last_elevation_image = cv2.imread(path)
                self.reload_elevation_image()

                return self.last_elevation_image
            else:
                return None

    def reload_elevation_image(self, combat_mode:bool=False):
        if combat_mode:
            self.last_elevation_image = take_screenshot()

        if self.last_elevation_image is None:
            print("No Elevation Image")
            return

        game_elevation_mark_image = self.last_elevation_image.copy()
        cx, cy = HeightDetector.get_center_point(game_elevation_mark_image)
        game_elevation_mark_image = HeightDetector.cut_x_line(game_elevation_mark_image, cx, 50)
        rcx, rcy = HeightDetector.get_center_point(game_elevation_mark_image)

        game_hsv_mask = self.mark_detector.get_hsv_mask(game_elevation_mark_image,
                        self.get_color(), cut_borders=False)

        height,width = game_hsv_mask.shape[:2]
        cut_y = round(height*0.1)
        MarkDetector.replace_area_with_black(game_hsv_mask, (0, 0), (width, cut_y))

        game_mark_pos = self.mark_detector.get_mark_positions(game_hsv_mask,
            self.app_ui.mark_max_radius_slider.get())[0]
        self.set_calculation_data(center_point=(cx, cy))
        if game_mark_pos is None:
            if self.is_dictor() and combat_mode:
                text_to_speech("No mark founded")
            self.set_calculation_data(elevation=0,corrected_distance=0,elevation_mark_point=(cx,cy))
        else:
            self.last_elevation_point1 = (cx, cy)
            self.last_elevation_point2 = game_mark_pos

            elevation = round(HeightDetector.get_elevation(cy, game_mark_pos[1], 90, self.last_distance))
            corrected_distance = round(HeightDetector.get_correct_distance(elevation, self.last_distance))
            if self.is_dictor() and combat_mode:
                text_to_speech(f"Elevation is {elevation}")
                text_to_speech(f"Corrected Distance is {corrected_distance}")
                
            self.set_calculation_data(elevation=elevation,
                elevation_mark_point=game_mark_pos, corrected_distance=corrected_distance)
        
        if self.app_ui.elevation_draw_processed_checkbox.get():
            draw_image = cv2.cvtColor(game_hsv_mask, cv2.COLOR_GRAY2BGR)
        else:
            draw_image = game_elevation_mark_image

        if self.app_ui.elevation_draw_points_checkbox.get():
            if game_mark_pos is not None:
                cv2.circle(draw_image, game_mark_pos, 2, (0, 255, 0), 5)
                cv2.arrowedLine(draw_image, (rcx, rcy), game_mark_pos, (0, 255, 0), 2)
            cv2.circle(draw_image, (rcx, rcy), 2, (0, 255, 0), 5)

        cut_top = int(self.last_elevation_image.shape[0]*0.45)

        self.app_ui.elevation_image.set_cv2(draw_image[cut_top:])

    def set_calculation_data(self, grid_gap:int|None=None,
                               player_pos:tuple[int, int]|None=None,
                               mark_pos:tuple[int, int]|None=None,
                               distance:float|None=None,
                               center_point:tuple[int, int]|None=None,
                               elevation_mark_point:tuple[int, int]|None=None,
                               elevation:float|None=None,
                               corrected_distance:float|None=None):
        if grid_gap is not None:
            self.app_ui.map_calculation_grid_gap_label.configure(text=f'{grid_gap} px')
        if mark_pos is not None:
            self.app_ui.map_calculation_mark_cordinates_label.configure(text=f'{mark_pos}')
        if player_pos is not None:
            self.app_ui.map_calculation_player_cordinates_label.configure(text=f'{player_pos}')
        if distance is not None:
            self.app_ui.map_calculation_distance_label.configure(text=f'{distance} m')
        if elevation is not None:
            self.app_ui.elevation_calculation_elevation_label.configure(text=f'{elevation} m')
        if center_point is not None:
            self.app_ui.elevation_calculation_center_cordinates_label.configure(
                text=f'{center_point}')
        if elevation_mark_point is not None:
            self.app_ui.elevation_calculation_mark_cordinates_label.configure(
                text=f'{elevation_mark_point}')
        if corrected_distance is not None:
            self.app_ui.elevation_calculation_elevated_distance_label.configure(
                text=f'{round(corrected_distance)} m')

    def get_color(self) -> str:
        return self.app_ui.mark_color_combobox.get()

    def is_dictor(self) -> bool:
        return self.app_ui.general_settings_dictor_checkbox.get()