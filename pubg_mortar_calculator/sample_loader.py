import cv2
import os
import numpy as np
import json

from .utils import paths
from datetime import datetime

class SampleLoader:
    def __init__(self):
        self.sample_units = []
    
    def add(self, player_position: tuple[int, int]|None=None,
            mark_position: tuple[int, int]|None=None, grid_gap:int=0,
            distance:int=0, elevation: int=0, corrected_distance: int=0,
            elevation_mark_position:tuple[int, int]|None=None,
            map_image:np.ndarray|None=None,
            elevation_image:np.ndarray|None=None
            ):
        file_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        path = os.path.join(paths.test_samples(), file_name)
        os.mkdir(path)
        with open(os.path.join(path, 'data.json'),
                  'w') as file:
            json.dump({
                'player_position':player_position,
                'mark_position':mark_position,
                'grid_gap':grid_gap,
                'distance':distance,
                'elevation':elevation,
                'corrected_distance':corrected_distance,
                'elevation_mark_position':elevation_mark_position
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
    