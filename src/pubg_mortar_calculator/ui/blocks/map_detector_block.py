import customtkinter as ct

from src.customtkinter_widgets import Checkbox, Combobox, Slider


class MapDetectorBlock(ct.CTkFrame):
    def __init__(self, master, on_update, on_map_preview, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.draw_checkbox = Checkbox(
            self,
            text="Draw Marks",
            command=on_update,
            saving_id="map_detection_draw_checkbox",
            default=True,
        ).grid(row=0, column=0, padx=5, pady=5)

        self.show_processed_image_checkbox = Checkbox(
            self,
            text="Draw Processed",
            command=on_update,
            saving_id="map_detection_show_processed_image_checkbox",
        ).grid(row=0, column=1, padx=5, pady=5)

        self.zoom_to_points_checkbox = Checkbox(
            self,
            text="Zoom To Points",
            command=on_update,
            saving_id="map_detection_zoom_to_points_checkbox",
            default=True,
        ).grid(row=1, column=0, padx=5)

        self.minimap_detection = Checkbox(
            self,
            text="Minimap Detection",
            command=on_update,
            saving_id="map_detection_minimap_detection",
        ).grid(row=1, column=1, padx=5)

        ct.CTkLabel(self, text="Mark Color: ").grid(row=2, column=0, padx=5, pady=5)

        self.color_combobox = Combobox(
            self,
            values=["orange", "yellow", "blue", "green"],
            command=on_update,
            return_value=False,
            saving_id="map_detection_color_combobox",
        )
        self.color_combobox.grid(row=2, column=1, padx=5, pady=5)

        self.max_radius_slider = Slider(
            self,
            "Mark Max Radius",
            "map_detection_max_radius_slider",
            5,
            50,
            default=30,
            command=lambda: on_update(),
        )
        self.max_radius_slider.grid(row=3, column=0, columnspan=2)

        self.debug_load_map_preview_button = ct.CTkButton(
            self, text="Load Map Preview", command=on_map_preview
        )
        self.debug_load_map_preview_button.grid(row=4, columnspan=2)
