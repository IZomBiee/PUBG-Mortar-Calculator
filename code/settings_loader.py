import json
import tools 
from app import App
from profile_loader import ProfileLoader

@tools.singleton
class SettingsLoader:
    def __init__(self, app:App, settings_path:str, base_settings:dict):
        self.path = settings_path
        self.settings = base_settings
        self.app = app
        self._load()

    def __getitem__(self, key:str):
        return self.settings[key]
    
    def _load(self):
        try:
            with open(self.path, 'r') as file:
                self.settings = json.load(file)
        except FileNotFoundError:
            pass
    
    def _save(self):
        with open(self.path, 'w') as file:
            json.dump(self.settings, file, indent=4)
    
    def get(self) -> dict:
        return self.settings
    
    def set_current(self):
        self.app.autoshooting_checkbox.select() if self["autoshooting"] \
            else self.app.autoshooting_checkbox.deselect()
        
        self.app.dictor_checkbox.select() if self["dictor"] \
            else self.app.dictor_checkbox.deselect()
        
        self.app.preview_checkbox.select() if self["draw_lines"] \
            else self.app.preview_checkbox.deselect()
        
        self.app.image_threshold1_slider.configure(to=self["canny_threshold1_max"])
        self.app.image_threshold2_slider.configure(to=self["canny_threshold2_max"])
        self.app.image_line_threshold_slider.configure(to=self["line_threshold_max"])
        self.app.image_line_min_lenth_slider.configure(to=self["line_lenth_max"])
        self.app.image_line_max_gap_slider.configure(to=self["max_gap_max"])

        for name in ProfileLoader().list_profiles_name():
            tools.combobox_add_value(self.app.profile_combobox, name)
        if self["last_profile_name"] != None and self["last_profile_name"] in ProfileLoader().list_profiles_name():
            ProfileLoader().set_profile(self["last_profile_name"])
            self.app.profile_combobox.set(self["last_profile_name"])
        else: ProfileLoader().set_profile('default')

        if self["last_preview_path"] != None:
            self.app.load_image_to_preview(self["last_preview_path"])
        
        self.app.calculate_hotkey_entry.insert(0, self["hotkey"])
        self.app.load_player_color(self["last_color"])
        self.app.player_color_combobox.set(self["last_color"])
        
    def save_current(self):
        self.settings = {
            "last_profile_name":self.app.profile_combobox.get(),
            "last_preview_path":self.app.last_preview_path,
            "autoshooting":self.app.autoshooting_checkbox.get(),
            "dictor":self.app.dictor_checkbox.get(),
            "draw_lines":self.app.preview_checkbox.get(),
            "canny_threshold1_max":self.app.image_threshold1_slider._to,
            "canny_threshold2_max":self.app.image_threshold2_slider._to,
            "line_threshold_max":self.app.image_line_threshold_slider._to,
            "line_lenth_max":self.app.image_line_min_lenth_slider._to,
            "max_gap_max":self.app.image_line_max_gap_slider._to,
            "hotkey":self.app.calculate_hotkey_entry.get(),
            "last_color":self.app.player_color_combobox.get()
        }
        self._save()

