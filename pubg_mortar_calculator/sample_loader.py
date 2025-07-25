import cv2
import numpy as np
import json
import os

from datetime import datetime
class SampleLoader:
    def __init__(self):
        self.samples_path = 'tests/test_samples/'
        self.samples = []
    
    def add(self, player_position:tuple[int, int],
                mark_position:tuple[int, int], grid_gap:int,
                color:str, frame:np.ndarray|None=None, name:str|None=None):
        
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
                'color':color
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

if __name__ == '__main__':
    sample_loader = SampleLoader()
    # sample_loader.add(np.array((255, 255, 3)), (0, 0), (0, 0), (52, 52), 'red', 'full')
    # sample_loader.change('2025-03-10_17-29-25.json', {'name':"Why so sireous"})