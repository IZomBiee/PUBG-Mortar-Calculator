import json
from pubg_mortar_calculator import utils

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pubg_mortar_calculator.app import App

@utils.singleton
class SettingsLoader:
    def __init__(self, app: "App", settings_path:str, base_settings:dict):
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
        
    def save_current_settings(self):
        self.settings = {
            "last_preview_path":self.app.last_preview_path,
            "autoshooting":self.app.general_settings_autoshooting_checkbox.get(),
            "dictor":self.app.general_settings_dictor_checkbox.get(),
            "draw_lines":self.app.processing_draw_lines_checkbox.get(),
            "show_gray":self.app.processing_show_gray_checkbox.get(),
            "hotkey":self.app.general_settings_hotkey_entry.get(),
            "last_color":self.app.detection_color_combobox.get(),
        }
        self._save()

    def load_settings(self):
        self.app.processing_draw_lines_checkbox.select() if self.settings['draw_lines'] else self.app.processing_draw_lines_checkbox.deselect()
        self.app.processing_show_gray_checkbox.select() if self.settings['show_gray'] else self.app.processing_show_gray_checkbox.deselect()
        self.app.general_settings_autoshooting_checkbox.select() if self.settings['dictor'] else self.app.general_settings_autoshooting_checkbox.deselect()
        self.app.general_settings_hotkey_entry.insert(0, self.settings['hotkey'])
        if self.settings['last_color'] != '':
            self.app.detection_color_combobox.set(self.settings['last_color'])
        self.app.general_settings_dictor_checkbox.select() if self['autoshooting'] else self.app.general_settings_dictor_checkbox.deselect()
        if self.settings['last_preview_path'] is not None:
            self.app.on_preview_image_load(self.settings['last_preview_path'])


