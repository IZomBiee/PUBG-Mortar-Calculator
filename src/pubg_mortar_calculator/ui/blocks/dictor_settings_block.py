import customtkinter as ct

from pubg_mortar_calculator.dictor_manager import DictorManager
from src.customtkinter_widgets import Checkbox, Slider


class DictorSettingsBlock(ct.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.columnconfigure(0, weight=1)

        self.dictor_checkbox = Checkbox(
            self,
            text="Dictor",
            saving_id="general_settings_dictor_checkbox",
            default=True,
        ).grid(row=0, column=0)

        self.volume_slider = Slider(
            self,
            "Volume",
            "dictor_settings_volume_slider",
            0,
            100,
            50,
            command=lambda volume: setattr(DictorManager(), "volume", volume / 100),
            return_value=True,
        )
        self.volume_slider.grid(row=1, column=0)

        self.rate_slider = Slider(
            self,
            "Rate",
            "dictor_settings_rate_slider",
            50,
            300,
            150,
            command=lambda rate: setattr(DictorManager(), "rate", rate),
            return_value=True,
        )
        self.rate_slider.grid(row=2, column=0)
