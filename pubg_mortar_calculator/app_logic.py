import cv2
import os
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .app import App

from .utils import imgpr, paths, take_game_screenshot
from .detectors import GridDetector,\
MapDetector, MarkDetector, GridDetector,\
HeightDetector
from .sample_loader import SampleLoader
from .dictor_manager import DictorManager


class AppLogic():
    def __init__(self, app_ui: "App"):
        self.app_ui: "App" = app_ui

        self.last_map_image: np.ndarray | None = None
        self.last_distance = 0
        self.last_grid_gap = 0
        self.last_player_position = None
        self.last_mark_position = None

        self.last_elevation_image: np.ndarray|None = None
        self.last_corrected_distance = 0
        self.last_elevation = 0
        self.last_elevation_mark_position = None

        self.grid_detector = GridDetector()
        self.mark_detector = MarkDetector()
        self.sample_loader = SampleLoader()
        self.map_detector = MapDetector()

        self.dictor_manager = DictorManager()
        self.dictor_manager.start()

        self.initialize_preview_images()
    
    def initialize_preview_images(self):
        if os.path.exists(paths.map_preview()):
            self.load_map_image(paths.map_preview())
        
        if os.path.exists(paths.elevation_preview()):
            self.load_elevation_image(paths.elevation_preview())

    def load_map_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = paths.get_image()
            if path == '':
                return None
            else:
                self.last_map_image = cv2.imread(path)
                cv2.imwrite(paths.map_preview(), self.last_map_image)
                self.process_map_image()
                return self.last_map_image
        else:
            if os.path.exists(path):
                self.last_map_image = cv2.imread(path)
                self.process_map_image()
                return self.last_map_image
            else:
                return None
    
    def load_elevation_image(self, path: str | None = None) -> np.ndarray | None:
        if path is None:
            path = paths.get_image()
            if path == '':
                return None
            else:
                self.last_elevation_image = cv2.imread(path)
                self.process_elevation_image()
                cv2.imwrite(paths.elevation_preview(),
                            self.last_elevation_image)

                return self.last_elevation_image
        else:
            if os.path.exists(path):
                self.last_elevation_image = cv2.imread(path)
                self.process_elevation_image()

                return self.last_elevation_image
            else:
                return None

    def calculate_map_in_combat(self):
        self.last_map_image = take_game_screenshot()
        self.process_map_image()
        if self.is_dictor():
            if self.last_distance != 0:
                self.dictor_manager.add(f'Line of Sight {self.last_distance}')
            else: self.dictor_manager.add(f'No Distance')
        cv2.imwrite(paths.map_preview(), self.last_map_image)
    
    def calculate_elevation_in_combat(self):
        self.last_elevation_image = take_game_screenshot()
        self.process_elevation_image()
        if self.last_elevation != 0:
            if self.is_dictor():
                self.dictor_manager.add(f'Elevation {self.last_elevation}')

                self.dictor_manager.add(f'Corrected {self.last_corrected_distance}')


            if self.app_ui.general_settings_add_to_test_samples_checkbox.get():
                self.sample_loader.add(
                    self.last_player_position, self.last_mark_position,
                    self.last_grid_gap, self.last_distance,
                    self.last_elevation, self.last_corrected_distance,
                    self.last_elevation_mark_position,
                    self.last_map_image, self.last_elevation_image
                )
        else:
            self.dictor_manager.add(f'No Elevation')

        cv2.imwrite(paths.elevation_preview(), self.last_elevation_image)

    def process_map_image(self):
        if self.last_map_image is None: return
            
        processed_image = self.last_map_image.copy()

        # Avoiding danger zones
        height , width = processed_image.shape[:2]
        imgpr.replace_area_with_black(processed_image, (0, int(height*0.85)),
            (int(width*0.15), height))
        if self.app_ui.map_detection_minimap_detection.get():
            minimap_detections = self.map_detector.detect(processed_image)
            processed_image = self.map_detector.cut_to_map(processed_image)
        if not self.app_ui.map_detection_minimap_detection.get() or\
            not len(minimap_detections):
            imgpr.replace_area_with_black(processed_image, (int(width*0.75),
                int(height*0.8)), (width, height))

        canny_image = self.grid_detector.get_canny_frame(processed_image,
            self.app_ui.grid_detection_canny1_threshold_slider.get(),
            self.app_ui.grid_detection_canny2_threshold_slider.get())

        self.grid_detector.detect_lines(canny_image,
            self.app_ui.grid_detection_line_threshold_slider.get()/100,
            self.app_ui.grid_detection_line_gap_slider.get()/100)
        
        grid_gap = self.grid_detector.calculate_grid_gap(
            self.app_ui.grid_detection_gap_threshold_slider.get())

        hsv_mask = self.mark_detector.get_hsv_mask(processed_image,
                                                   self.get_color())

        player_pos, mark_pos = self.mark_detector.get_mark_positions(hsv_mask,
            self.app_ui.map_detection_max_radius_slider.get())
        
        if player_pos is not None and mark_pos is not None and \
            grid_gap != 0:
            distance = round(self.grid_detector.get_distance(
                player_pos, mark_pos, grid_gap))
        else: distance = 0

        if self.app_ui.grid_detection_show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2BGR)

        elif self.app_ui.map_detection_show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.grid_detection_draw_grid_lines_checkbox.get():
            self.grid_detector.draw_lines(processed_image)

        if self.app_ui.map_detection_draw_checkbox.get():
            self.mark_detector.draw_marks(processed_image)

        if mark_pos is not None and player_pos is not None \
        and self.app_ui.map_detection_zoom_to_points_checkbox.get():
            processed_image = imgpr.cut_to_points(processed_image,
                mark_pos, player_pos)

        self.app_ui.map_image.set_cv2(processed_image)
        self.process_elevation_image()
        self.set_map_data(grid_gap=grid_gap, player_pos=player_pos,
                                    mark_pos=mark_pos, distance=distance)

    def process_elevation_image(self):
        if self.last_elevation_image is None: return

        processed_image = self.last_elevation_image.copy()

        cut_y = int(processed_image.shape[0]*0.2)
        processed_image = processed_image[cut_y:
            processed_image.shape[0]-cut_y]
        
        center = imgpr.get_center_point(processed_image)
        processed_image = imgpr.cut_x_line(processed_image, center[0], 0.01)
        cutted_center = imgpr.get_center_point(processed_image)

        hsv_mask_image = self.mark_detector.get_hsv_mask(processed_image)
        mark_position = self.mark_detector.get_mark_positions(
            hsv_mask_image, self.app_ui.map_detection_max_radius_slider.get())[0]

        if mark_position is None or self.last_distance == 0: elevation = 0
        elif self.last_distance is not None:
            elevation = HeightDetector.get_elevation(
                center[1], mark_position[1], 90, self.last_distance)

        corrected_distance = round(HeightDetector.get_correct_distance(
            elevation, self.last_distance))
        
        if self.app_ui.elevation_draw_processed_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask_image, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.elevation_draw_points_checkbox.get():
            cv2.circle(processed_image, cutted_center, 2, (0, 255, 0), 5)
            if mark_position is not None:
                cv2.arrowedLine(processed_image, cutted_center, mark_position,
                                (0, 255, 0), 3)
                cv2.circle(processed_image, mark_position, 2, (0, 255, 0), 5)

        self.set_elevation_data(center_point=center,
            elevation_mark_point=mark_position, elevation=round(elevation),
            corrected_distance=corrected_distance)
        
        self.app_ui.elevation_image.set_cv2(processed_image)

    def set_elevation_data(self,
        center_point:tuple[int, int]|None=None,
        elevation_mark_point:tuple[int, int]|None=None,
        elevation:int=0,
        corrected_distance:int=0):
        self.last_corrected_distance = corrected_distance
        self.last_elevation = elevation
        self.last_elevation_mark_position = elevation_mark_point

        self.app_ui.elevation_calculation_elevation_label.configure(text=f'{elevation} m')
        self.app_ui.elevation_calculation_center_cordinates_label.configure(
            text=f'{center_point}')

        self.app_ui.elevation_calculation_mark_cordinates_label.configure(
            text=f'{elevation_mark_point}')
        self.app_ui.elevation_calculation_elevated_distance_label.configure(
            text=f'{round(corrected_distance)} m')

    def set_map_data(self, grid_gap:int=0,
                               player_pos:tuple[int, int]|None=None,
                               mark_pos:tuple[int, int]|None=None,
                               distance:float=0):
        if self.last_distance != distance:
            self.last_distance=round(distance)
            self.process_elevation_image()
        
        self.last_grid_gap = grid_gap
        self.last_player_position = player_pos
        self.last_mark_position = mark_pos

        self.app_ui.map_calculation_grid_gap_label.configure(text=f'{grid_gap} px')
        self.app_ui.map_calculation_mark_cordinates_label.configure(text=f'{mark_pos}')
        self.app_ui.map_calculation_player_cordinates_label.configure(text=f'{player_pos}')
        self.app_ui.map_calculation_distance_label.configure(text=f'{distance} m')

    def get_color(self) -> str:
        return self.app_ui.map_detection_color_combobox.get()

    def is_dictor(self) -> bool:
        return self.app_ui.general_settings_dictor_checkbox.get()