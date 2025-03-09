import cv2
import numpy as np
import json

from datetime import datetime
class SampleLoader:
    def __init__(self):
        self.samples_path = 'tests/test_samples/'
    
    def add(self, frame:np.ndarray, player_position:list[int, int],
                mark_position:list[int, int], grid_gap:list[int, int],
                color:str, map_borders:list[int, int, int, int]):
        time = str(datetime.now())

        cv2.imwrite(time+'.png', frame)

        with open(self.samples_path+time+'.json', 'w') as file:
            json.dump({
                'frame_path':self.samples_path+time+'.png',
                'player_position':player_position,
                'mark_position':mark_position,
                'grid_gap':grid_gap,
                'color':color,
                'map_borders':map_borders
            }, file)

    def load(self, name:str) -> dict:
        with open(self.samples_path+name, 'r') as file:
            return json.load(file)
        