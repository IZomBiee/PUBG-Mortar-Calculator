import json
from pubg_mortar_calculator import utils

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pubg_mortar_calculator.app import App

@utils.singleton
class SettingsLoader:
    def __init__(self, app: "App", settings_path:str):
        self.path = settings_path
        self.settings = {
            "last_preview_path":None,
            "dictor":1,
            "draw_grid_lines":1,
            "line_threshold":1700,
            "line_gap":150,
            "gap_threshold":50,
            "show_processed_image":0,
            "canny1_threshold":20,
            "canny2_threshold":40,
            "calculation_key":"ctrl+k",
            "last_color":"orange",  
            "draw_marks":1,
            "add_to_test_samples":0,
        }
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
            "dictor":self.app.general_settings_dictor_checkbox.get(),
            "draw_grid_lines":self.app.grid_detection_draw_grid_lines_checkbox.get(),
            "line_threshold":self.app.grid_detection_line_threshold_slider.get(),
            "line_gap":self.app.grid_detection_line_gap_slider.get(),
            "gap_threshold":self.app.grid_detection_gap_threshold_slider.get(),
            "show_processed_image":self.app.grid_detection_show_processed_image_checkbox.get(),
            "canny1_threshold":self.app.grid_detection_canny1_threshold_slider.get(),
            "canny2_threshold":self.app.grid_detection_canny2_threshold_slider.get(),
            "calculation_key":self.app.general_settings_calculation_key_entry.get(),
            "last_color":self.app.mark_color_combobox.get(),
            "draw_marks":self.app.mark_draw_checkbox.get(),
            "add_to_test_samples":self.app.general_settings_add_to_test_samples_checkbox.get(),
        }
        self._save()

    def load_settings(self):
        self.app.grid_detection_draw_grid_lines_checkbox.select() if self.settings['draw_grid_lines'] else self.app.grid_detection_draw_grid_lines_checkbox.deselect()
        self.app.grid_detection_show_processed_image_checkbox.select() if self.settings['show_processed_image'] else self.app.grid_detection_show_processed_image_checkbox.deselect()
        self.app.general_settings_dictor_checkbox.select() if self.settings['dictor'] else self.app.general_settings_dictor_checkbox.deselect()
        self.app.general_settings_calculation_key_entry.insert(0, self.settings['calculation_key'])
        if self.settings['last_color'] != '':
            self.app.mark_color_combobox.set(self.settings['last_color'])
        self.app.general_settings_add_to_test_samples_checkbox.select() \
        if self.settings['add_to_test_samples'] else \
            self.app.general_settings_add_to_test_samples_checkbox.deselect()

        self.app.mark_draw_checkbox.select() \
        if self.settings['draw_marks'] else \
            self.app.mark_draw_checkbox.deselect()

        self.app.grid_detection_canny1_threshold_slider.set(self.settings['canny1_threshold'])
        self.app.grid_detection_canny2_threshold_slider.set(self.settings['canny2_threshold'])
        self.app.grid_detection_line_threshold_slider.set(self.settings['line_threshold'])
        self.app.grid_detection_line_gap_slider.set(self.settings['line_gap'])
        self.app.grid_detection_gap_threshold_slider.set(self.settings['gap_threshold'])
        
        if self.settings['last_preview_path'] is not None:
            self.app.on_preview_image_load(self.settings['last_preview_path'])


