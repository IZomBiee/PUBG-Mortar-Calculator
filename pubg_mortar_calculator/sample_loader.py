import cv2
import numpy as np
import json

from datetime import datetime

class SampleLoader:
    def __init__(self):
        self.samples_path = 'tests/test_samples/'
        self.samples = []
    
    def add(self, player_position:tuple[int, int] | None,
                mark_position:tuple[int, int] | None, grid_gap:int | None,
                color:str, frame:np.ndarray|None=None, name:str|None=None, real_distance: int | None = None):
        
        if name is None:
            time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else: time = name

        if frame is not None:
            cv2.imwrite(self.samples_path+time+'.png', frame)

        with open(self.samples_path+time+'.json', 'w') as file:
            json.dump({
                'name': time,
                'player_position':player_position,
                'mark_position':mark_position,
                'grid_gap':grid_gap,
                'color':color,
                'real_distance':real_distance
            }, file)

    def change(self, name:str, data:dict):
        if not name.endswith('.json'): name += '.json'
        try:
            with open(self.samples_path+name, 'r') as file:
                previous_data = json.load(file)
        except FileNotFoundError:
            previous_data = {}

        with open(self.samples_path+name, 'w') as file:
            for key in data.keys():
                previous_data[key] = data[key]
            json.dump(previous_data, file)

    def load(self, name:str) -> dict:
        with open(self.samples_path+name+'.json', 'r') as file:
            return json.load(file)