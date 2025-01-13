import json
import tools
import os
import pathlib
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import App

@tools.singleton
class ProfileLoader:
    def __init__(self, app: "App", profiles_folder_path:str, default_profile:dict):
        self.profiles_path = profiles_folder_path 
        self.default_profile = default_profile
        self.last_profile_name = 'default'
        self.last_profile = self.default_profile
        self.app = app
        self.check_default_profile()
        
    def check_default_profile(self):
        if 'default' not in self.list_profiles_name():
            self._save_profile('default', self.default_profile)
        else:
            self.default_profile = self._load_profile('default')

    def _load_profile(self, name: str) -> dict:
        path = self.profiles_path + name + '.json'
        try:
            with open(path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("EROR")
            raise FileNotFoundError(f"Profile {name} can't be founded in {self.profiles_path}")
        return data

    def _save_profile(self, name:str, profile:dict):
        path = self.profiles_path + name + '.json'
        with open(path, 'w') as file:
            json.dump(profile, file, indent=4)
    
    def list_profiles_name(self) -> list[str]:
        names = []
        for file in os.listdir(self.profiles_path):
            if file.endswith('.json'):
                names.append(''.join(file.split('/')[-1].split('.')[0:-1]))
        return names

    def create_new_profile(self, name:str):
        self._save_profile(name, self.default_profile)
        self.set_profile('default')

    def delete_profile(self, name:str):
        path = self.profiles_path + name + '.json'
        os.remove(path) 
        if self.last_profile_name == name:
            self.last_profile_name = 'default'

    def set_profile(self, name:str) -> dict:
        self.save_current_profile()
        profile = self._load_profile(name)
        self.app.image_threshold1_slider.set(profile["canny_threshold1"])
        self.app.image_threshold2_slider.set(profile["canny_threshold2"])
        self.app.image_line_threshold_slider.set(profile["line_threshold"])
        self.app.image_line_min_lenth_slider.set(profile["line_lenth"])
        self.app.image_line_max_gap_slider.set(profile["max_gap"])

        self.app.image_threshold1_label.configure(text=profile["canny_threshold1"])
        self.app.image_threshold2_label.configure(text=profile["canny_threshold2"])
        self.app.image_line_threshold_label.configure(text=profile["line_threshold"])
        self.app.image_line_min_lenth_label.configure(text=profile["line_lenth"])
        self.app.image_line_max_gap_label.configure(text=profile["max_gap"])
        self.last_profile_name = name
        self.last_profile = profile
    
    
    def save_current_profile(self):
        profile = {
            "canny_threshold1":int(self.app.image_threshold1_slider.get()),
            "canny_threshold2":int(self.app.image_threshold2_slider.get()),
            "line_threshold":int(self.app.image_line_threshold_slider.get()),
            "line_lenth":int(self.app.image_line_min_lenth_slider.get()),
            "max_gap":int(self.app.image_line_max_gap_slider.get())
        }
        self._save_profile(self.last_profile_name, profile)

