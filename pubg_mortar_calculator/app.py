import customtkinter as ct

from .custom_widgets import *
from .app_logic import AppLogic 

class App(ct.CTk, AppLogic):
    def __init__(self):
        ct.CTk.__init__(self)
        self.title("PUBG-Morta-Calculator")
        
        title_font = ct.CTkFont('Arial', 15, 'bold')

        # Left Frame
        self.left_frame = ct.CTkFrame(self)
        self.left_frame.grid(row=0, column=0)

        self.map_image = CustomImage(self.left_frame,
            (int(720/1.2), int(480//1.2)),
            save_aspect_ratio=True).grid(row=0, column=0)

        # Map Calculation Frame 
        self.map_calculation_frame = ct.CTkFrame(self.left_frame)
        self.map_calculation_frame.grid(row=1, column=0)
        
        ct.CTkLabel(self.map_calculation_frame, text='Calculated Map Data',
                    font=title_font).grid(row=1, column=0, columnspan=4)

        ct.CTkLabel(self.map_calculation_frame,text='Player Cordinates: '
                    ).grid(row=2, column=0)

        self.map_calculation_player_cordinates_label = ct.CTkLabel(
            self.map_calculation_frame, text='None')
        self.map_calculation_player_cordinates_label.grid(row=2, column=1)
        
        ct.CTkLabel(self.map_calculation_frame,
            text='Mark Cordinates: ').grid(row=3, column=0)

        self.map_calculation_mark_cordinates_label = ct.CTkLabel(
            self.map_calculation_frame, text='None')
        self.map_calculation_mark_cordinates_label.grid(row=3, column=1)
        
        ct.CTkLabel(self.map_calculation_frame, text='Grid Gap: '
                    ).grid(row=4, column=0)

        self.map_calculation_grid_gap_label = ct.CTkLabel(
            self.map_calculation_frame, text='None')
        self.map_calculation_grid_gap_label.grid(row=4, column=1)

        ct.CTkLabel(self.map_calculation_frame, text='Distance: '
                    ).grid(row=5, column=0)

        self.map_calculation_distance_label = ct.CTkLabel(
            self.map_calculation_frame, text='0')
        self.map_calculation_distance_label.grid(row=5, column=1)

        # Center Frame
        self.center_frame = ct.CTkFrame(self, fg_color='transparent')
        self.center_frame.grid(row=0, column=1)

        # Grid Detection Frame
        self.grid_detection_frame = ct.CTkFrame(self.center_frame)
        self.grid_detection_frame.grid(row=0, column=0, pady=10, padx=5)
        
        ct.CTkLabel(self.grid_detection_frame, text="Grid Detector",
                    font=title_font).grid(row=0, column=0, columnspan=3)

        self.grid_detection_show_processed_image_checkbox = CustomCheckbox(
            self.grid_detection_frame, text='Draw Processed',
            command=self.process_map_image,
            saving_id='grid_detection_show_processed_image_checkbox'
            ).grid(row=1, column=0,  padx=(10, 0))

        self.grid_detection_draw_grid_lines_checkbox = CustomCheckbox(
            self.grid_detection_frame, text='Draw Grid',
            command=self.process_map_image,
            saving_id='grid_detection_draw_grid_lines_checkbox'
            ).grid(row=1, column=1)

        self.grid_detection_canny1_threshold_slider = CustomSlider(
            self.grid_detection_frame, "Canny 1 Threshold", 0, 100,
            number_of_steps=100, default=20,command=self.process_map_image,
            return_value=False, saving_id='grid_detection_canny1_threshold_slider')
        self.grid_detection_canny1_threshold_slider.grid(row=2, column=0)

        self.grid_detection_canny2_threshold_slider = CustomSlider(
            self.grid_detection_frame, "Canny 2 Threshold", 0, 100,
            number_of_steps=100, default=40,command=self.process_map_image,
            return_value=False, saving_id='grid_detection_canny2_threshold_slider')
        self.grid_detection_canny2_threshold_slider.grid(row=3, column=0)

        self.grid_detection_line_threshold_slider = CustomSlider(
            self.grid_detection_frame, "Line Threshold", 20, 100,
            number_of_steps=100, default=40,command=self.process_map_image,
            return_value=False, saving_id='grid_detection_line_threshold_slider')
        self.grid_detection_line_threshold_slider.grid(row=4, column=0)

        self.grid_detection_line_gap_slider = CustomSlider(
            self.grid_detection_frame, "Line Gap", 0, 100,
            number_of_steps=100, default=40,command=self.process_map_image,
            return_value=False, saving_id='grid_detection_line_gap_slider')
        self.grid_detection_line_gap_slider.grid(row=5, column=0)

        self.grid_detection_gap_threshold_slider = CustomSlider(
            self.grid_detection_frame, "Gap Threshold", 0, 50,
            number_of_steps=50, default=30,command=self.process_map_image,
            return_value=False, saving_id='grid_detection_gap_threshold_slider')
        self.grid_detection_gap_threshold_slider.grid(row=6, column=0)

        self.grid_detection_load_example_button = ct.CTkButton(
            self.grid_detection_frame, text='Load Example Image',
            command=self.load_map_image)
        self.grid_detection_load_example_button.grid(row=7, column=0,
            columnspan=3, pady=(0, 10))

        # Map Detection Frame
        self.map_detection_frame = ct.CTkFrame(self.center_frame)
        self.map_detection_frame.grid(row=1, column=0)

        ct.CTkLabel(self.map_detection_frame, text='Map Detector',
                    font=title_font).grid(row=0, column=0, columnspan=3)

        self.map_detection_draw_checkbox = CustomCheckbox(
            self.map_detection_frame, text="Draw Marks",
            command=self.process_map_image,
            saving_id='map_detection_draw_checkbox'
            ).grid(row=1, column=0, padx=(10, 10))
        
        self.map_detection_show_processed_image_checkbox = CustomCheckbox(
            self.map_detection_frame, text="Draw Processed",
            command=self.process_map_image,
            saving_id='map_detection_show_processed_image_checkbox'
            ).grid(row=1, column=1, padx=(10, 10))
        
        self.map_detection_zoom_to_points_checkbox = CustomCheckbox(
            self.map_detection_frame, text="Zoom To Points",
            command=self.process_map_image,
            saving_id='map_detection_zoom_to_points_checkbox'
            ).grid(row=2, padx=(10, 10))

        self.map_detection_minimap_detection = CustomCheckbox(
            self.map_detection_frame, text="Minimap Detection",
            command=self.process_map_image,
            saving_id='map_detection_minimap_detection'
            ).grid(row=2, column=1, padx=(10, 10))

        ct.CTkLabel(self.map_detection_frame, text="Mark Color: "
                    ).grid(row=3, column=0)

        self.map_detection_color_combobox = CustomCombobox(
            self.map_detection_frame, values=['orange', 'yellow', 'blue', 'green'],
            command=self.process_map_image, return_value=False,
            saving_id="map_detection_color_combobox")
        self.map_detection_color_combobox.grid(row=3, column=1, columnspan=2)

        self.map_detection_max_radius_slider = CustomSlider(
            self.map_detection_frame, "Mark Max Radius", 5, 50,
            default=30, number_of_steps=45,
            command=self.process_map_image,
            return_value=False, saving_id='map_detection_max_radius_slider'
            ).grid(row=4)
        
        # Elevation Frame
        self.elevation_frame = ct.CTkFrame(self.center_frame)
        self.elevation_frame.grid(row=2, column=0, pady=(10, 10))

        ct.CTkLabel(self.elevation_frame, text='Height Detector',
                    font=title_font).grid(row=0, column=0, columnspan=2)
        
        self.elevation_draw_points_checkbox = CustomCheckbox(
            self.elevation_frame, text="Draw Points",
            command=self.process_elevation_image,
            saving_id='elevation_draw_points_checkbox'
            ).grid(row=1, column=0, padx=(10, 10))

        self.elevation_draw_processed_checkbox = CustomCheckbox(
            self.elevation_frame, text="Draw Processed",
            command=self.process_elevation_image,
            saving_id='elevation_draw_processed_checkbox'
            ).grid(row=1, column=1, padx=(10, 10))

        ct.CTkLabel(self.elevation_frame,
            text='Elevation Hotkey:  ').grid(row=2, column=0)

        self.elevation_hotkey_entry = CustomEntry(
            self.elevation_frame, 'pageup',
            'Elevation Hotkey',
            saving_id='elevation_hotkey_entry'
            ).grid(row=2, column=1)
        
        self.elevation_load_example_button = ct.CTkButton(
            self.elevation_frame, text='Load Example Image',
            command=self.load_elevation_image)
        self.elevation_load_example_button.grid(row=3, column=0,
            columnspan=2, pady=(0, 10))

        # General Settings Frame
        self.general_settings_frame = ct.CTkFrame(self.center_frame)
        self.general_settings_frame.grid(row=4, column=0)

        ct.CTkLabel(self.general_settings_frame, text='General Settings',
                    font=title_font).grid(row=0, column=0, columnspan=2)

        self.general_settings_dictor_checkbox = CustomCheckbox(
            self.general_settings_frame,text="Dictor",
            saving_id='general_settings_dictor_checkbox').grid(row=1, column=0)
        
        self.general_settings_add_to_test_samples_checkbox = CustomCheckbox(
            self.general_settings_frame, text="Add To Test Samples",
            saving_id='general_settings_add_to_test_samples_checkbox'
            ).grid(row=1, column=1, padx=(0, 5))

        ct.CTkLabel(self.general_settings_frame, text='Calculation Hotkey:'
            ).grid(row=3, column=0, padx=5, pady=5)

        self.general_settings_calculation_hotkey_entry = CustomEntry(
            self.general_settings_frame, text='pagedown',
            saving_id='general_settings_calculation_hotkey_entry')
        self.general_settings_calculation_hotkey_entry.grid(row=3, column=1)

        # Right Frame
        self.right_frame = CTkFrame(self)
        self.right_frame.grid(row=0, column=2)

        self.elevation_image = CustomImage(self.right_frame,
            (int(100), int(480//1.2)), save_aspect_ratio=True
            ).grid(row=0, column=0)

        # Elevation Calculation Frame 
        self.elevation_calculation_frame = ct.CTkFrame(self.right_frame)
        self.elevation_calculation_frame.grid(row=1, column=0)
        
        ct.CTkLabel(self.elevation_calculation_frame,
            text='Calculated Elevation Data',
            font=title_font
            ).grid(row=1, column=0, columnspan=4)

        ct.CTkLabel(self.elevation_calculation_frame,
                    text='Center Cordinates: ').grid(row=2, column=0)

        self.elevation_calculation_center_cordinates_label = ct.CTkLabel(
            self.elevation_calculation_frame, text='None')
        self.elevation_calculation_center_cordinates_label.grid(row=2, column=1)
        
        ct.CTkLabel(self.elevation_calculation_frame,
            text='Mark Cordinates: ').grid(row=3, column=0)

        self.elevation_calculation_mark_cordinates_label = ct.CTkLabel(
            self.elevation_calculation_frame, text='None')
        self.elevation_calculation_mark_cordinates_label.grid(row=3, column=1)
        
        ct.CTkLabel(self.elevation_calculation_frame,
            text='Elevation: ').grid(row=4, column=0)

        self.elevation_calculation_elevation_label = ct.CTkLabel(
            self.elevation_calculation_frame, text='None')
        self.elevation_calculation_elevation_label.grid(row=4, column=1)

        ct.CTkLabel(self.elevation_calculation_frame,
            text='Elevated Distance: ').grid(row=5, column=0)

        self.elevation_calculation_elevated_distance_label = ct.CTkLabel(
            self.elevation_calculation_frame, text='0')
        self.elevation_calculation_elevated_distance_label.grid(row=5, column=1)
        
        self.app_ui = self
        AppLogic.__init__(self, self.app_ui)

    def get_calculation_key(self) -> str:
        return self.general_settings_calculation_hotkey_entry.get()
    
    def get_elevation_key(self) -> str:
        return self.elevation_hotkey_entry.get()