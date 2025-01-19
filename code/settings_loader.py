import json
import tools 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import App
    from profile_loader import ProfileLoader

@tools.singleton
class SettingsLoader:
    def __init__(self, app: "App", profile_loader: "ProfileLoader",settings_path:str, base_settings:dict):
        self.path = settings_path
        self.settings = base_settings
        self.app = app
        self.profile_loader = profile_loader
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
            "last_profile_name":self.app.profile_combobox.get(),
            "last_preview_path":self.app.last_preview_path,
            "autoshooting":self.app.general_settings_autoshooting_checkbox.get(),
            "dictor":self.app.general_settings_dictor_checkbox.get(),
            "draw_lines":self.app.processing_draw_lines_checkbox.get(),
            "show_gray":self.app.processing_show_gray_checkbox.get(),
            "hotkey":self.app.general_settings_hotkey_entry.get(),
            "mark_is_cursor":self.app.general_settings_mark_is_cursor_checkbox.get(),
            "last_color":self.app.detection_color_combobox.get(),
        }
        self._save()

    def load_settings(self):
        for profile in self.profile_loader.get_all_profile_names():
            self.app.profile_combobox.add_values(profile)
        if self['last_profile_name'] is not None:
            try:
                self.profile_loader.set_profile(self['last_profile_name'])
                self.app.profile_combobox.set(self['last_profile_name'])
            except KeyError:
                self.profile_loader.set_profile('default')
                self.app.profile_combobox.set('default')
        else: self.app.profile_combobox.set('default')

        self.app.processing_draw_lines_checkbox.select() if self.settings['draw_lines'] else self.app.processing_draw_lines_checkbox.deselect()
        self.app.processing_show_gray_checkbox.select() if self.settings['show_gray'] else self.app.processing_show_gray_checkbox.deselect()
        self.app.general_settings_autoshooting_checkbox.select() if self.settings['dictor'] else self.app.general_settings_autoshooting_checkbox.deselect()
        self.app.general_settings_hotkey_entry.insert(0, self.settings['hotkey'])
        if self.settings['last_color'] != '':
            self.app.detection_color_combobox.set(self.settings['last_color'])
        self.app.load_player_color(self.app.detection_color_combobox.get())
        self.app.general_settings_dictor_checkbox.select() if self['autoshooting'] else self.app.general_settings_dictor_checkbox.deselect()
        self.app.general_settings_mark_is_cursor_checkbox.select() if self['mark_is_cursor'] else self.app.general_settings_mark_is_cursor_checkbox.deselect()
        if self.settings['last_preview_path'] is not None:
            self.app.on_preview_image_load(self.settings['last_preview_path'])


