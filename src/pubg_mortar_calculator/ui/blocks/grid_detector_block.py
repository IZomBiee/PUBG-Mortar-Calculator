from src.customtkinter_widgets import *
from src.customtkinter_widgets import TitledBlock

class GridDetectorBlock(TitledBlock):
    def __init__(self, master, on_slider_update, *args, **kwargs):
        super().__init__(master, "Grid Detector", *args, **kwargs)
        on_update = lambda *args: on_slider_update()
        grid = self.get_grid()

        self.show_processed_image_checkbox = Checkbox(
            grid, text='Draw Processed',
            command=on_update,
            saving_id='grid_detection_show_processed_image_checkbox'
            ).grid(row=0, column=0, padx=(10, 0))

        self.draw_grid_lines_checkbox = Checkbox(
            grid, text='Draw Grid',
            command=on_update,
            saving_id='grid_detection_draw_grid_lines_checkbox',
            default=True
            ).grid(row=0, column=1)

        self.canny1_threshold_slider = Slider(
            grid, "Canny 1 Threshold", 'grid_detection_canny1_threshold_slider', 0, 100,
            default=20, command=on_update)
        self.canny1_threshold_slider.grid(row=1, column=0, columnspan=2)

        self.canny2_threshold_slider = Slider(
            grid, "Canny 2 Threshold", 'grid_detection_canny2_threshold_slider',
            0, 100, default=40, command=on_update)
        self.canny2_threshold_slider.grid(row=2, column=0, columnspan=2)

        self.line_threshold_slider = Slider(
            grid, "Line Threshold", 'grid_detection_line_threshold_slider',
            20, 100, default=40,command=on_update)
        self.line_threshold_slider.grid(row=3, column=0, columnspan=2)

        self.line_gap_slider = Slider(
            grid, "Line Gap", 'grid_detection_line_gap_slider', 0, 100,
            default=40,command=on_update)
        self.line_gap_slider.grid(row=4, column=0, columnspan=2)

        self.gap_threshold_slider = Slider(
            grid, "Gap Threshold", 'grid_detection_gap_threshold_slider', 0, 50,
            default=30,command=on_update)
        self.gap_threshold_slider.grid(row=5, column=0, columnspan=2)