import cv2
import os
import numpy as np
import json
import shutil
from .utils import paths
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Sample:
    map_image: np.ndarray
    elevation_image: np.ndarray
    map_player_position:tuple[int, int]
    map_mark_position:tuple[int, int]
    elevation_mark_position:tuple[int, int]
    grid_gap:int
    elevation:float
    color:str
    map_box:tuple[int, int, int, int]|None=field(default=None)

    def save_to_folder(self, path:str):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        data = {}
        cv2.imwrite(os.path.join(path, 'map.png'), self.map_image)
        cv2.imwrite(os.path.join(path, 'elevation.png'), self.elevation_image)
        data['map_player_position'] = self.map_player_position
        data['map_mark_position'] = self.map_mark_position
        data['elevation_mark_position'] = self.elevation_mark_position
        data['grid_gap'] = self.grid_gap
        data['elevation'] = self.elevation
        data['color'] = self.color
        data['map_box'] = self.map_box
        with open(os.path.join(path, 'data.json'), 'w') as file:
            json.dump(data, file)

    def __eq__(self, other):
        if not isinstance(other, Sample):
            return False
        return (
            np.array_equal(self.map_image, other.map_image) and
            np.array_equal(self.elevation_image, other.elevation_image) and
            self.map_player_position == other.map_player_position and
            self.map_mark_position == other.map_mark_position and
            self.elevation_mark_position == other.elevation_mark_position and
            self.grid_gap == other.grid_gap and
            self.elevation == other.elevation and
            self.color == other.color and
            self.map_box == other.map_box
        )

    @staticmethod
    def __parse_map_box(data:dict) -> tuple[int, int, int, int]|None:
        if data.get("map_box") is not None:
            box = data["map_box"]
        elif data.get("minimap_box") is not None:
            box = data["minimap_box"]
        else:
            box = None
        return box

    @staticmethod
    def load_from_folder(path:str) -> "Sample":
        with open(os.path.join(path, 'data.json'), 'r') as file:
            data: dict = json.load(file)
        return Sample(
            cv2.imread(os.path.join(path, 'map.png')),
            cv2.imread(os.path.join(path, 'elevation.png')),
            data['player_position'] if data.get('map_player_position') is None else data['map_player_position'],
            data['mark_position'] if data.get('map_mark_position') is None else data['map_mark_position'],
            data['elevation_mark_position'],
            data['grid_gap'],
            data['elevation'],
            'yellow' if data.get('color') is None else data['color'],
            Sample.__parse_map_box(data)
        )

class SampleManager:
    def __init__(self):
        self.samples: list[Sample] = []
        self.paths: list[str] = []
    
    def add(self, sample:Sample):
        file_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S-%f")
        path = os.path.join(paths.test_samples(), file_name)
        self.paths.append(path)
        sample.save_to_folder(path)
        self.samples.append(sample)

    def load(self):
        for dir in os.listdir(paths.test_samples()):
            path = os.path.join(paths.test_samples(), dir)
            self.paths.append(path)
            self.samples.append(Sample.load_from_folder(path))

    def delete(self, sample: Sample) -> Sample:
        index = self.samples.index(sample)
        deleted_sample = self.samples.pop(index)
        deleted_path = self.paths.pop(index)
        shutil.rmtree(deleted_path)
        return deleted_sample

    def __len__(self) -> int:
        return len(self.samples)
    
    def __iter__(self):
        return iter(self.samples)
    
if __name__ == '__main__':
    sample_manager = SampleManager()
    sample_manager.load()
    for item in sample_manager:
        print(item)
        exit()