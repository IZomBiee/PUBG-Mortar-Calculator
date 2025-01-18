import json
import tools
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import App

@tools.singleton
class ProfileLoader:
    def __init__(self, app: "App", path:str,base_profile:dict):
        self.app = app
        self.base_profile = base_profile
        self.path = path
        self.profiles = {'default':self.base_profile.copy()}
        self.last_profile_name = 'default'
        self._load()
    
    def __getitem__(self, key:str):
        return self.profiles[key]

    def _load(self):
        try:
            with open(self.path, 'r') as file:
                self.profiles = json.load(file)
        except FileNotFoundError:
            pass

    def _save(self):
        with open(self.path, 'w') as file:
            json.dump(self.profiles, file)
    
    def save_all_profiles(self):
        self.save_current_to_profile(self.last_profile_name)
        self._save()

    def get_all_profile_names(self) -> list:
        return [key for key in self.profiles] 

    def save_current_to_profile(self, name:str):
        self[name]["canny_threshold1"] = self.app.processing_threshold1_slider.get()
        self[name]["canny_threshold2"] = self.app.processing_threshold2_slider.get()
        self[name]["line_threshold"] = self.app.processing_line_threshold_slider.get()
        self[name]["line_lenth"] = self.app.processing_line_min_lenth_slider.get()
        self[name]["max_gap"] = self.app.processing_max_gap_slider.get()
        self._save()
    
    def change_profile(self, name:str):
        self.save_current_to_profile(self.last_profile_name)
        self.last_profile_name = name
        self.set_profile(name)
    
    def set_profile(self, name:str):
        self.app.profile_combobox.set(name)
        self.app.processing_threshold1_slider.set(self[name]["canny_threshold1"])
        self.app.processing_threshold2_slider.set(self[name]["canny_threshold2"])
        self.app.processing_line_threshold_slider.set(self[name]["line_threshold"])
        self.app.processing_line_min_lenth_slider.set(self[name]["line_lenth"])
        self.app.processing_max_gap_slider.set(self[name]["max_gap"])
        self.last_profile_name = name
    
    def create_profile(self, name:str, from_base=False):
        self.save_current_to_profile(self.last_profile_name)
        if from_base:
            self.app.processing_threshold1_slider.set(self['default']["canny_threshold1"])
            self.app.processing_threshold2_slider.set(self['default']["canny_threshold2"])
            self.app.processing_line_threshold_slider.set(self['default']["line_threshold"])
            self.app.processing_line_min_lenth_slider.set(self['default']["line_lenth"])
            self.app.processing_max_gap_slider.set(self['default']["max_gap"])
        self.profiles[name] = self.base_profile.copy()
        self.app.profile_combobox.add_values(name)
        self.set_profile(name)
            
    def delete_profile(self, name:str):
        self.profiles.pop(name)
        self.app.profile_combobox.remove_value(name)
        self.set_profile('default')
        