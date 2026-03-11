import customtkinter as ct

from src.customtkinter_widgets import Checkbox, Slider


class GridDetectorBlock(ct.CTkFrame):
    def __init__(self, master, on_slider_update, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.grid_columnconfigure([0, 1], weight=1)
        self.grid_rowconfigure([0, 1, 2, 3, 4, 5], weight=1)

        def on_update(*args):
            return on_slider_update()

        self.show_processed_image_checkbox = Checkbox(
            self,
            text="Draw Processed",
            command=on_update,
            saving_id="grid_detection_show_processed_image_checkbox",
        ).grid(row=0, column=0, padx=(10, 0))

        self.draw_grid_lines_checkbox = Checkbox(
            self,
            text="Draw Grid",
            command=on_update,
            saving_id="grid_detection_draw_grid_lines_checkbox",
            default=True,
        ).grid(row=0, column=1)

        self.canny1_threshold_slider = Slider(
            self,
            "Canny 1 Threshold",
            "grid_detection_canny1_threshold_slider",
            0,
            100,
            default=20,
            command=on_update,
        )
        self.canny1_threshold_slider.grid(row=1, column=0, columnspan=2, sticky="e")

        self.canny2_threshold_slider = Slider(
            self,
            "Canny 2 Threshold",
            "grid_detection_canny2_threshold_slider",
            0,
            100,
            default=40,
            command=on_update,
        )
        self.canny2_threshold_slider.grid(row=2, column=0, columnspan=2, sticky="e")

        self.line_threshold_slider = Slider(
            self,
            "Line Threshold",
            "grid_detection_line_threshold_slider",
            20,
            100,
            default=40,
            command=on_update,
        )
        self.line_threshold_slider.grid(row=3, column=0, columnspan=2, sticky="e")

        self.line_gap_slider = Slider(
            self,
            "Line Gap",
            "grid_detection_line_gap_slider",
            0,
            100,
            default=40,
            command=on_update,
        )
        self.line_gap_slider.grid(row=4, column=0, columnspan=2, sticky="e")

        self.line_merge_threshold_slider = Slider(
            self,
            "Merge Threshold",
            "grid_detection_merge_threshold_slider",
            0,
            50,
            default=10,
            command=on_update,
        )
        self.line_merge_threshold_slider.grid(row=5, column=0, columnspan=2, sticky="e")
