import cv2
import os
import numpy as np
import json

from .utils import paths
from datetime import datetime

class SampleLoader:
    def __init__(self):
        self.sample_units = []
    
    def add(self, map_image: np.ndarray, elevation_image: np.ndarray,
        map_player_position:tuple[int, int], map_mark_position:tuple[int, int],
        elevation_mark_position:tuple[int, int],
        grid_gap:int, elevation:float, color:str, 
        minimap_box:tuple[int, int, int, int]|None=None):
        file_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        path = os.path.join(paths.test_samples(), file_name)
        os.mkdir(path)
        with open(os.path.join(path, 'data.json'),
                  'w') as file:
            json.dump({
                'player_position':map_player_position,
                'mark_position':map_mark_position,
                'elevation_mark_position':elevation_mark_position,
                'grid_gap':grid_gap,
                'elevation':elevation,
                'color':color,
                'minimap_box':minimap_box
            }, file)

        if map_image is not None:
            cv2.imwrite(os.path.join(path, 'map.png'), map_image)    
        if elevation_image is not None:
            cv2.imwrite(os.path.join(path, 'elevation.png'), elevation_image)    

    def load(self):
        for dir in os.listdir(paths.test_samples()):
            dir = os.path.join(paths.test_samples(), dir)
            with open(os.path.join(dir, 'data.json'), 'r') as file:
                map_image_path = os.path.join(dir, 'map.png')
                elevation_image_path = os.path.join(dir, 'elevation.png')
                self.sample_units.append(
                {
                    'path':dir,
                    'data':json.load(file),
                    'map_image': cv2.imread(map_image_path)
                    if os.path.exists(map_image_path) else None,
                    'elevation_image':cv2.imread(elevation_image_path)
                    if os.path.exists(elevation_image_path) else None,
                }
                )

    def __len__(self) -> int:
        return len(self.sample_units)
    
    def __iter__(self):
        return iter(self.sample_units)
    