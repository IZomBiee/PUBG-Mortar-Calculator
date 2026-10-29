import customtkinter as ct

from pubg_mortar_calculator.customtkinter_widgets import Checkbox, Combobox, Slider


class MarkDetectorBlock(ct.CTkFrame):
    def __init__(self, master, on_update, on_map_preview, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.columnconfigure([0, 1], weight=1)
        self.rowconfigure([0, 1, 2, 3], weight=1)

        self.draw_checkbox = Checkbox(
            self,
            text="Draw Marks",
            command=on_update,
            saving_id="mark_detection_draw_checkbox",
            default=True,
        ).grid(row=0, column=0, padx=5, pady=5)

        self.show_processed_image_checkbox = Checkbox(
            self,
            text="Draw Processed",
            command=on_update,
            saving_id="mark_detection_show_processed_image_checkbox",
        ).grid(row=0, column=1, padx=5, pady=5)

        self.zoom_to_points_checkbox = Checkbox(
            self,
            text="Zoom To Points",
            command=on_update,
            saving_id="mark_detection_zoom_to_points_checkbox",
            default=False,
        ).grid(row=1, column=0, padx=5)

        self.yolo_checkbox = Checkbox(
            self,
            text="Use Yolo",
            command=on_update,
            saving_id="mark_detection_yolo_checkbox",
            default=True,
        ).grid(row=1, column=1, padx=5)

        ct.CTkLabel(self, text="Mark Color: ").grid(row=2, column=0, padx=5, pady=5)

        self.color_combobox = Combobox(
            self,
            values=["yellow", "orange", "blue", "green"],
            command=on_update,
            return_value=False,
            saving_id="mark_detection_color_combobox",
        )
        self.color_combobox.set("yellow")
        self.color_combobox.grid(row=2, column=1, padx=5, pady=5)

        self.min_radius_slider = Slider(
            self,
            "Mark Min Radius",
            "mark_detection_min_radius_slider",
            0,
            50,
            default=5,
            command=lambda: on_update(),
        )
        self.min_radius_slider.grid(row=3, column=0, columnspan=2)

        self.max_radius_slider = Slider(
            self,
            "Mark Max Radius",
            "mark_detection_max_radius_slider",
            5,
            50,
            default=25,
            command=lambda: on_update(),
        )
        self.max_radius_slider.grid(row=4, column=0, columnspan=2)

        self.debug_load_map_preview_button = ct.CTkButton(
            self, text="Load Map Preview", command=on_map_preview
        )
        self.debug_load_map_preview_button.grid(row=5, columnspan=2)
