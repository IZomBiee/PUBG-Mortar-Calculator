import customtkinter as ct

from pubg_mortar_calculator.customtkinter_widgets import Checkbox, Slider


class MinimapDetectorBlock(ct.CTkFrame):
    def __init__(self, master, on_update, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.columnconfigure([0, 1], weight=1)
        self.rowconfigure([0, 1, 2, 3], weight=1)

        self.enabled_checkbox = Checkbox(
            self,
            text="Enabled",
            command=on_update,
            saving_id="minimap_detector_enabled_checkbox",
            default=True,
        ).grid(row=0, column=0)

        self.offset_slider = Slider(
            self,
            "Offset",
            "minimap_detector_offset_slider",
            0,
            1000,
            170,
            command=on_update,
        )
        self.offset_slider.grid(row=1, column=0)

        self.small_minimap_size_slider = Slider(
            self,
            "Small Minimap Size",
            "minimap_detector_small_minimap_size_slider",
            100,
            1000,
            673,
            command=on_update,
        )
        self.small_minimap_size_slider.grid(row=2, column=0)

        self.large_minimap_size_slider = Slider(
            self,
            "Large Minimap Size",
            "minimap_detector_large_minimap_size_slider",
            100,
            1000,
            715,
            command=on_update,
        )
        self.large_minimap_size_slider.grid(row=3, column=0)
