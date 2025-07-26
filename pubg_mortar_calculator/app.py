import customtkinter as ct

from pubg_mortar_calculator.app_logic import AppLogic
from pubg_mortar_calculator.custom_widgets import *
from pubg_mortar_calculator.grid_detector import GridDetector
from pubg_mortar_calculator.mark_detector import MarkDetector
from pubg_mortar_calculator.sample_loader import SampleLoader

class App(ct.CTk, AppLogic):
    def __init__(self):
        ct.CTk.__init__(self)
        AppLogic.__init__(self)
        self.title("PUBG-Morta-Calculator")
        
        title_font = ct.CTkFont('Arial', 15, 'bold')

        # Preview Frame
        self.preview_frame = ct.CTkFrame(self)
        self.preview_frame.grid(row=0, column=0)

        self.preview_image = CustomImage(self.preview_frame, (720, 480), save_aspect_ratio=True).grid(row=0, column=0)

        # Calculation Frame 
        self.calculation_frame = ct.CTkFrame(self.preview_frame)
        self.calculation_frame.grid(row=1, column=0)
        
        ct.CTkLabel(self.calculation_frame, text='Calculated values',
                    font=title_font).grid(row=1, column=0, columnspan=2)

        ct.CTkLabel(self.calculation_frame,text='Player Cordinates: ').grid(row=2, column=0)

        self.calculation_player_cordinates_label = ct.CTkLabel(self.calculation_frame, text='None')
        self.calculation_player_cordinates_label.grid(row=2, column=1)
        
        ct.CTkLabel(self.calculation_frame, text='Mark Cordinates: ').grid(row=3, column=0)

        self.calculation_mark_cordinates_label = ct.CTkLabel(self.calculation_frame, text='None')
        self.calculation_mark_cordinates_label.grid(row=3, column=1)
        
        ct.CTkLabel(self.calculation_frame, text='Grid Gap: ').grid(row=4, column=0)

        self.calculation_grid_gap_label = ct.CTkLabel(self.calculation_frame, text='None')
        self.calculation_grid_gap_label.grid(row=4, column=1)

        ct.CTkLabel(self.calculation_frame, text='Distance: ').grid(row=5, column=0)

        self.calculation_distance_label = ct.CTkLabel(self.calculation_frame, text='None')
        self.calculation_distance_label.grid(row=5, column=1)

        # Right Frame
        self.right_frame = ct.CTkFrame(self, fg_color='transparent')
        self.right_frame.grid(row=0, column=1)

        # Grid Detection Frame
        self.grid_detection_frame = ct.CTkFrame(self.right_frame)
        self.grid_detection_frame.grid(row=1, column=0, pady=10, padx=5)
        
        ct.CTkLabel(self.grid_detection_frame, text="Grid Detection",
                    font=title_font).grid(row=0, column=0, columnspan=3)

        self.grid_detection_show_processed_image_checkbox = CustomCheckbox(self.grid_detection_frame, text='Show Processed Image',
                                                          command=self.reload_preview_image).grid(row=1, column=0,  padx=(10, 0))

        self.grid_detection_draw_grid_lines_checkbox = CustomCheckbox(self.grid_detection_frame, text='Draw Grid Lines',
                                                    command=self.reload_preview_image).grid(row=1, column=1)

        self.grid_detection_canny1_threshold_slider = CustomSlider(self.grid_detection_frame, "Canny 1 Threshold", 0, 300,
                                                               number_of_steps=100, command=self.reload_preview_image, return_value=False)
        self.grid_detection_canny1_threshold_slider.grid(row=2, column=0)

        self.grid_detection_canny2_threshold_slider = CustomSlider(self.grid_detection_frame, "Canny 2 Threshold", 0, 300,
                                                               number_of_steps=100, command=self.reload_preview_image, return_value=False)
        self.grid_detection_canny2_threshold_slider.grid(row=3, column=0)

        self.grid_detection_line_threshold_slider = CustomSlider(self.grid_detection_frame, "Line Threshold", 500, 2500,
                                                                number_of_steps=300, command=self.reload_preview_image, return_value=False)
        self.grid_detection_line_threshold_slider.grid(row=4, column=0)

        self.grid_detection_line_gap_slider = CustomSlider(self.grid_detection_frame, "Line Gap", 50, 500,
                                                                number_of_steps=100, command=self.reload_preview_image, return_value=False)
        self.grid_detection_line_gap_slider.grid(row=5, column=0)

        self.grid_detection_gap_threshold_slider = CustomSlider(self.grid_detection_frame, "Gap Threshold", 0, 50,
                                                                number_of_steps=50, command=self.reload_preview_image, return_value=False)
        self.grid_detection_gap_threshold_slider.grid(row=6, column=0)

        self.grid_detection_load_example_button = ct.CTkButton(self.grid_detection_frame, text='Load Example Image',
                                                command=self.load_preview_image)
        self.grid_detection_load_example_button.grid(row=7, column=0, columnspan=3, pady=(0, 10))

        # General Settings Frame
        self.general_settings_frame = ct.CTkFrame(self.right_frame)
        self.general_settings_frame.grid(row=3, column=0, pady=10)

        ct.CTkLabel(self.general_settings_frame, text='General Settings',
                    font=title_font).grid(row=0, column=0, columnspan=2)

        self.general_settings_dictor_checkbox = CustomCheckbox(
            self.general_settings_frame,text="Dictor").grid(row=1, column=0)
        
        self.general_settings_add_to_test_samples_checkbox = CustomCheckbox(
            self.general_settings_frame, text="Add To Test Samples").grid(row=1, column=1, padx=(0, 5))

        ct.CTkLabel(self.general_settings_frame, text='Calculation Hotkey:').grid(row=3, column=0, padx=5, pady=5)

        self.general_settings_calculation_key_entry = CustomEntry(self.general_settings_frame, placeholder_text="Example ctrl+2")
        self.general_settings_calculation_key_entry.grid(row=3, column=1)

        # Mark Frame
        self.mark_frame = ct.CTkFrame(self.right_frame)
        self.mark_frame.grid(row=4, column=0)

        ct.CTkLabel(self.mark_frame, text='Mark Detection',
                    font=title_font).grid(row=0, column=0, columnspan=3)

        self.mark_draw_checkbox = CustomCheckbox(self.mark_frame, text="Draw Marks Location",
                                  command=self.reload_preview_image).grid(row=1, column=0, padx=(10, 10))
        
        self.mark_show_processed_image_checkbox = CustomCheckbox(self.mark_frame, text="Show Processed Image",
                            command=self.reload_preview_image).grid(row=1, column=1, padx=(10, 10))
        
        ct.CTkLabel(self.mark_frame, text="Mark Color: ").grid(row=2, column=0)

        self.mark_color_combobox = CustomCombobox(self.mark_frame, values=['orange', 'yellow', 'blue', 'green'],
                                                       command=self.reload_preview_image, return_value=False,
                                                       settings_id="Mark Color Combobox")
        self.mark_color_combobox.grid(row=2, column=1)
        
        self.app_ui = self
        self.on_ui_load()

    def get_calculation_key(self) -> str:
        return self.general_settings_calculation_key_entry.get()