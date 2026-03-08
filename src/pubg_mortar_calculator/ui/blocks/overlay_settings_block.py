from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class OverlaySettingsBlock(TitledBlock):
    def __init__(self, master, on_checkbox, *args, **kwargs):
        super().__init__(master, "Overlay Settings", *args, **kwargs)
        grid = self.get_grid()

        grid.grid_columnconfigure(0, weight=1)

        self.enabled_checkbox = Checkbox(
            grid, text="Enabled",
            saving_id='overlay_settings_enabled_checkbox', command=on_checkbox,
            ).grid(row=0, column=0, padx=5, pady=5)