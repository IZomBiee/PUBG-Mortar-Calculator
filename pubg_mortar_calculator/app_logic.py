import cv2
import os
import numpy as np
import tkinter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui.app import App

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
        self.last_minimap_box = None

        self.last_elevation_image: np.ndarray|None = None
        self.last_corrected_distance = 0
        self.last_elevation = 0
        self.last_elevation_mark_position = None

        print("Load grid detector...")
        self.grid_detector = GridDetector()
        print("Load mark detector...")
        self.mark_detector = MarkDetector()
        print("Load sample loader...")
        self.sample_loader = SampleLoader()
        print("Load map detector...")
        if os.path.exists(paths.map_detection_model()):
            self.map_detector = MapDetector()
        else:
            print(f"Can't find minimap detection model at "+
                  paths.map_detection_model())
            self.map_detector = None
            self.app_ui.map_detector_block.minimap_detection.\
            checkbox.configure(state=tkinter.DISABLED)
            self.app_ui.map_detector_block.minimap_detection.set(False)
        
        print("Starting dictor manager...")
        self.dictor_manager = DictorManager(
            self.app_ui.dictor_settings_block.rate_slider.get(),
            self.app_ui.dictor_settings_block.volume_slider.get())
        self.dictor_manager.start()

        print("Loading preview...")
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

            if self.app_ui.general_settings_block.add_to_test_samples_checkbox.get():
                self.sample_loader.add(self.last_map_image,
                                    self.last_elevation_image,
                                    self.last_player_position,
                                    self.last_mark_position,
                                    self.last_elevation_mark_position,
                                    self.last_grid_gap,
                                    self.last_elevation,
                                    self.get_color(),
                                    self.last_minimap_box)

        else:
            self.dictor_manager.add(f'No Elevation')

        cv2.imwrite(paths.elevation_preview(), self.last_elevation_image)

    def process_map_image(self):
        if self.last_map_image is None: return
            
        processed_image = self.last_map_image.copy()

        if self.app_ui.map_detector_block.minimap_detection.get()\
        and self.map_detector is not None:
            self.last_minimap_box = self.map_detector.detect(processed_image)
            if self.last_minimap_box is not None:
                x0, y0, x1, y1 = self.last_minimap_box
                processed_image = imgpr.cut_to_points(
                    processed_image, (x0, y0), (x1, y1), 0)
        else:
            minimap_detections = []
            self.last_minimap_box = None

        canny_image = self.grid_detector.get_canny_frame(processed_image,
            self.app_ui.grid_detector_block.canny1_threshold_slider.get(),
            self.app_ui.grid_detector_block.canny2_threshold_slider.get())

        self.grid_detector.detect_lines(canny_image,
            self.app_ui.grid_detector_block.line_threshold_slider.get()/100,
            self.app_ui.grid_detector_block.line_gap_slider.get()/100)
        
        grid_gap = self.grid_detector.calculate_grid_gap(
            self.app_ui.grid_detector_block.gap_threshold_slider.get())

        # Avoiding danger zones for mark detection
        height , width = processed_image.shape[:2]

        if not self.app_ui.map_detector_block.minimap_detection.get()\
        or self.last_minimap_box is None:
            imgpr.replace_area_with_black(processed_image, (0, int(height*0.83)),
                (int(width*0.13), height))
            imgpr.replace_area_with_black(processed_image, (int(width*0.75),
                int(height*0.8)), (width, height))

        hsv_mask = self.mark_detector.get_hsv_mask(processed_image,
                                                   self.get_color())

        player_pos, mark_pos = self.mark_detector.get_mark_positions(hsv_mask,
            self.app_ui.map_detector_block.max_radius_slider.get())
        
        if player_pos is not None and mark_pos is not None and \
            grid_gap != 0:
            distance = round(self.grid_detector.get_distance(
                player_pos, mark_pos, grid_gap))
        else: distance = 0

        if self.app_ui.grid_detector_block.show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2BGR)

        elif self.app_ui.map_detector_block.show_processed_image_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.grid_detector_block.draw_grid_lines_checkbox.get():
            self.grid_detector.draw_lines(processed_image)

        if self.app_ui.map_detector_block.draw_checkbox.get():
            self.mark_detector.draw_marks(processed_image)

        if mark_pos is not None and player_pos is not None \
        and self.app_ui.map_detector_block.zoom_to_points_checkbox.get():
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
        imgpr.replace_area_with_black(
            processed_image, (0, 0), (processed_image.shape[1], cut_y))
        
        center = imgpr.get_center_point(processed_image)
        processed_image = imgpr.cut_x_line(processed_image, center[0], 0.02)
        cutted_center = imgpr.get_center_point(processed_image)

        hsv_mask_image = self.mark_detector.get_hsv_mask(processed_image)
        mark_position = self.mark_detector.get_mark_positions(
            hsv_mask_image, self.app_ui.map_detector_block.max_radius_slider.get())[0]

        if mark_position is None or self.last_distance == 0: elevation = 0
        elif self.last_distance is not None:
            elevation = HeightDetector.get_elevation(
                center[1], mark_position[1], 90, self.last_distance)

        corrected_distance = round(HeightDetector.get_correct_distance(
            elevation, self.last_distance))
        
        if self.app_ui.elevation_detector_block.draw_processed_checkbox.get():
            processed_image = cv2.cvtColor(hsv_mask_image, cv2.COLOR_GRAY2BGR)
        
        if self.app_ui.elevation_detector_block.draw_points_checkbox.get():
            cv2.circle(processed_image, cutted_center, 2, (0, 255, 0), 5)
            if mark_position is not None:
                cv2.arrowedLine(processed_image, cutted_center, mark_position,
                                (0, 255, 0), 3)
                cv2.circle(processed_image, mark_position, 2, (0, 255, 0), 5)

        self.set_elevation_data(center_point=center,
            elevation_mark_point=mark_position, elevation=round(elevation),
            corrected_distance=corrected_distance)
        
        self.app_ui.elevation_image.set_cv2(
            processed_image[cut_y:processed_image.shape[0]])

    def set_elevation_data(self,
        center_point:tuple[int, int]|None=None,
        elevation_mark_point:tuple[int, int]|None=None,
        elevation:int=0,
        corrected_distance:int=0):
        self.last_corrected_distance = corrected_distance
        self.last_elevation = elevation
        self.last_elevation_mark_position = elevation_mark_point

        self.app_ui.elevation_data_block.set_value(
            'Mark Pos', str(elevation_mark_point))
        self.app_ui.elevation_data_block.set_value(
            'Elevation', str(elevation)+"m")
        self.app_ui.elevation_data_block.set_value(
            'Elevated Distance', str(corrected_distance)+"m")

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

        self.app_ui.map_data_block.set_value('Grid Gap', str(grid_gap)+"px")
        self.app_ui.map_data_block.set_value('Mark Pos', str(mark_pos))
        self.app_ui.map_data_block.set_value('Player Pos', str(player_pos))
        self.app_ui.map_data_block.set_value('Distance', str(distance)+"m")

    def get_color(self) -> str:
        return self.app_ui.map_detector_block.color_combobox.get()

    def is_dictor(self) -> bool:
        return self.app_ui.dictor_settings_block.dictor_checkbox.get()