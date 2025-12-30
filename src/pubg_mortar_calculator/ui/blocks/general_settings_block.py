import customtkinter as ct
from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class GeneralSettingsBlock(TitledBlock):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, "General Settings", *args, **kwargs)
        grid = self.get_grid()

        self.add_to_test_samples_checkbox = Checkbox(
            grid, text="Add To Test Samples",
            saving_id='general_settings_add_to_test_samples_checkbox'
            ).grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        ct.CTkLabel(grid, text='Calculation Hotkey:'
            ).grid(row=1, column=0, padx=5, pady=5)

        self.map_hotkey_entry = Entry(
            grid, text='pageup',
            saving_id='general_settings_calculation_hotkey_entry')
        self.map_hotkey_entry.grid(row=1, column=1, padx=5, pady=5)

        ct.CTkLabel(grid,
            text='Elevation Hotkey:  ').grid(row=2, column=0, padx=5, pady=5)

        self.elevation_hotkey_entry = Entry(
            grid, 'pagedown',
            'Elevation Hotkey',
            saving_id='elevation_hotkey_entry'
            ).grid(row=2, column=1, padx=5, pady=5)