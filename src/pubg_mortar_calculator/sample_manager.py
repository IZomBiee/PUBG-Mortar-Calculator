import cv2
import os
import numpy as np
import json
import shutil
from pathlib import Path
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
    color:str
    map_box:list[int]|None=field(default=None)
    name: str|None=field(default=None)
    verified:bool=field(default=False)

    def save_to_folder(self, path:str):
        if os.path.exists(path):
            shutil.rmtree(path)

        os.makedirs(path, exist_ok=True)
        data = {}

        cv2.imwrite(os.path.join(path, 'map.png'), self.map_image)
        cv2.imwrite(os.path.join(path, 'elevation.png'), self.elevation_image)
        data['map_player_position'] = self.map_player_position
        data['map_mark_position'] = self.map_mark_position
        data['elevation_mark_position'] = self.elevation_mark_position
        data['grid_gap'] = self.grid_gap
        data['color'] = self.color
        data['map_box'] = self.map_box
        data['verified'] = self.verified
        with open(os.path.join(path, 'data.json'), 'w') as file:
            json.dump(data, file)

    def get_minimap_image(self) -> np.ndarray:
        if self.map_box is not None:
            x0, y0, x1, y1 = self.map_box
            return self.map_image[y0:y1, x0:x1]
        return self.map_image

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
            self.color == other.color and
            self.map_box == other.map_box
        )

    @staticmethod
    def __parse_map_box(data:dict) -> list[int]|None:
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
            'yellow' if data.get('color') is None else data['color'],
            Sample.__parse_map_box(data),
            Path(path).name,
            data.get('verified', False)
        )

class SampleManager:
    def __init__(self):
        self.count = len(os.listdir(paths.test_samples()))
    
    def add(self, sample:Sample):
        folder_name = datetime.now().strftime("%d-%m-%Y")
        file_name = datetime.now().strftime("%H-%M-%S")
        path = os.path.join(paths.test_samples(), folder_name, file_name)
        sample.save_to_folder(path)
        self.count += 1

    def delete(self, name:str) -> Sample:
        for day in os.listdir(paths.test_samples()):
            day_path = os.path.join(paths.test_samples(), day)
            if not os.path.isdir(day_path):
                continue

            for sample_name in os.listdir(day_path):
                if sample_name == name:
                    sample_path = os.path.join(day_path, sample_name)
                    sample = Sample.load_from_folder(sample_path)
                    shutil.rmtree(sample_path)
                    self.count -= 1
                    return sample
                
        raise IndexError(f"No sample {name} was found")
    
    def _iter_samples(self):
            for day in os.listdir(paths.test_samples()):
                day_path = os.path.join(paths.test_samples(), day)
                if not os.path.isdir(day_path):
                    continue

                for sample_name in os.listdir(day_path):
                    yield Sample.load_from_folder(
                        os.path.join(day_path, sample_name)
                    )

    def __len__(self) -> int:
        return self.count
    
    def __iter__(self):
        return iter(self._iter_samples())


    def __getitem__(self, index: int):
        all_samples = []
        for day in os.listdir(paths.test_samples()):
            day_path = os.path.join(paths.test_samples(), day)
            if not os.path.isdir(day_path):
                continue

            for sample_name in os.listdir(day_path):
                all_samples.append(os.path.join(day_path, sample_name))

        return Sample.load_from_folder(all_samples[index])
    
if __name__ == '__main__':
    sample_manager = SampleManager()
    for item in sample_manager:
        print(item)