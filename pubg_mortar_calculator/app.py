import customtkinter
import cv2
import mouse
import time
import json
from pubg_mortar_calculator import utils
from pubg_mortar_calculator.custom_widgets import *
from pubg_mortar_calculator.grid_detector import GridDetector
from pubg_mortar_calculator.mark_detector import MarkDetector
from pubg_mortar_calculator.sample_loader import SampleLoader

@utils.singleton
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("PUBG-Morta-Calculator")

        self.last_preview_path = None
        self.last_image = None

        self.is_full_map = False
        self.is_large_minimap = False

        # Preview Frame
        self.preview_frame = customtkinter.CTkFrame(self)
        self.preview_frame.grid(row=0, column=0)

        self.preview_image = CustomImage(self.preview_frame, (800, 600), save_aspect_ratio=True)
        self.preview_image.grid(row=0, column=0)

        # Calculation Frame 
        self.calculation_frame = customtkinter.CTkFrame(self.preview_frame)
        self.calculation_frame.grid(row=1, column=0)
        
        self.calculation_title_label = customtkinter.CTkLabel(self.calculation_frame, text='Calculated values')
        self.calculation_title_label.grid(row=1, column=0, columnspan=2)

        self.calculation_player_cordinates_describe_label = customtkinter.CTkLabel(self.calculation_frame, text='Player Cordinates: ')
        self.calculation_player_cordinates_describe_label.grid(row=2, column=0)

        self.calculation_player_cordinates_label = customtkinter.CTkLabel(self.calculation_frame, text='None')
        self.calculation_player_cordinates_label.grid(row=2, column=1)
        
        self.calculation_mark_cordinates_describe_label = customtkinter.CTkLabel(self.calculation_frame, text='Mark Cordinates: ')
        self.calculation_mark_cordinates_describe_label.grid(row=3, column=0)

        self.calculation_mark_cordinates_label = customtkinter.CTkLabel(self.calculation_frame, text='None')
        self.calculation_mark_cordinates_label.grid(row=3, column=1)
        
        self.calculation_grid_gap_describe_label = customtkinter.CTkLabel(self.calculation_frame, text='Grid Gap: ')
        self.calculation_grid_gap_describe_label.grid(row=4, column=0)

        self.calculation_grid_gap_label = customtkinter.CTkLabel(self.calculation_frame, text='None')
        self.calculation_grid_gap_label.grid(row=4, column=1)

        self.calculation_distance_describe_label = customtkinter.CTkLabel(self.calculation_frame, text='Distance: ')
        self.calculation_distance_describe_label.grid(row=5, column=0)

        self.calculation_distance_label = customtkinter.CTkLabel(self.calculation_frame, text='None')
        self.calculation_distance_label.grid(row=5, column=1)

        # Right Frame
        self.right_frame = customtkinter.CTkFrame(self, fg_color='transparent')
        self.right_frame.grid(row=0, column=1)

        # Processing Frame
        self.processing_frame = customtkinter.CTkFrame(self.right_frame)
        self.processing_frame.grid(row=1, column=0, pady=10)
        
        self.processing_title_label = customtkinter.CTkLabel(self.processing_frame, text="Image Processing Settings")
        self.processing_title_label.grid(row=0, column=1)

        self.processing_draw_lines_checkbox = customtkinter.CTkCheckBox(self.processing_frame, text='Draw Lines',
                                                          command=self.process_preview_image)
        self.processing_draw_lines_checkbox.grid(row=6, column=0)

        self.processing_load_example_button = customtkinter.CTkButton(self.processing_frame, text='Load Example Image',
                                                      command=self.on_preview_image_load)
        self.processing_load_example_button.grid(row=6, column=1)

        self.processing_show_gray_checkbox = customtkinter.CTkCheckBox(self.processing_frame, text='Show Gray',
                                                          command=self.process_preview_image)
        self.processing_show_gray_checkbox.grid(row=6, column=2)

        # General Settings Frame
        self.general_settings_frame = customtkinter.CTkFrame(self.right_frame)
        self.general_settings_frame.grid(row=2, column=0)

        self.general_settings_title_label = customtkinter.CTkLabel(self.general_settings_frame, text='General Settings')
        self.general_settings_title_label.grid(row=0, column=0, columnspan=2)

        self.general_settings_dictor_checkbox = customtkinter.CTkCheckBox(self.general_settings_frame, text="Dictor")
        self.general_settings_dictor_checkbox.grid(row=1, column=1)
        
        self.general_settings_add_to_test_samples_checkbox = customtkinter.CTkCheckBox(self.general_settings_frame, text="Add To Test Samples")
        self.general_settings_add_to_test_samples_checkbox.grid(row=2, column=1)

        self.general_settings_calculate_hotkey_describe_label = customtkinter.CTkLabel(self.general_settings_frame, text='Hotkey:') 
        self.general_settings_calculate_hotkey_describe_label.grid(row=3, column=0)

        self.general_settings_hotkey_entry = customtkinter.CTkEntry(self.general_settings_frame, placeholder_text="Example ctrl+2")
        self.general_settings_hotkey_entry.grid(row=3, column=1)

        # Player Frame
        self.detection_frame = customtkinter.CTkFrame(self.right_frame)
        self.detection_frame.grid(row=3, column=0)

        self.detection_title_label = customtkinter.CTkLabel(self.detection_frame, text='Player Color Settings')
        self.detection_title_label.grid(row=0, column=0)
        
        self.detection_color_combobox = CustomCombobox(self.detection_frame,
                                                       values=['orange', 'yellow', 'blue', 'green'],
                                                       command=self.process_preview_image, return_value=False)
        self.detection_color_combobox.grid(row=1, column=0)
        
        self.mark_detector = MarkDetector([3840, 2160])
        self.sample_loader = SampleLoader()

    def on_preview_image_load(self, path:str=None):
        if path is None:
            path = utils.get_image_path()
            if path == '':
                return
            else: self.last_preview_path = path
        else: self.last_preview_path = path
        if self.last_preview_path is not None:
            self.last_image = self.preview_image.set_path(self.last_preview_path)
            self.process_preview_image()

    def get_calculate_key(self):
        return self.general_settings_hotkey_entry.get()

    def get_full_map_toggle_key(self):
        return 'm'
    
    def get_large_minimap_toggle_key(self):
        return 'n'
    
    def toggle_minimap(self, set:bool=None):
        if set == None:
            self.is_large_minimap = not self.is_large_minimap
        else:
            self.is_large_minimap = set
        print(self.is_large_minimap)

    def toggle_map(self, set:bool=None):
        if set == None:
            self.is_full_map = not self.is_full_map
        else:
            self.is_full_map = set
        print(self.is_full_map)
        

    def process_preview_image(self, combat_mode=False):
        print(f'------------- CALCULATION IN {"COMBAT"if combat_mode else "PREVIEW"} MODE -------------')
        if combat_mode:
            self.last_image = utils.take_screenshot()
            cv2.imwrite(f'screenshots/{time.time()}.png', self.last_image)
        else:
            if self.last_image is None: return

        frame = self.last_image.copy()

        grid_detector = GridDetector()

        if not self.is_full_map and combat_mode:
            frame = grid_detector.get_minimap_frame(frame, self.is_large_minimap)

        grid_detector.detect_lines(frame)
        grid_gap = grid_detector.get_grid_gap()
            
        self.calculation_grid_gap_label.configure(text=f'{grid_gap}')
        print(f"GRID GAP: {grid_gap}")

        player_cord, mark_cord = self.mark_detector.get_cords(frame, self.detection_color_combobox.get())
        self.calculation_mark_cordinates_label.configure(text=f'{mark_cord}')
        self.calculation_player_cordinates_label.configure(text=f'{player_cord}')
        print(f'PLAYER POSITION: {player_cord}')
        print(f'MARK POSITION: {mark_cord}')

        try:
            distance = round(grid_detector.get_distance(player_cord, mark_cord, grid_gap))
        except ZeroDivisionError:
            distance = 0
        except TypeError:
            distance = 0
            
        self.calculation_distance_label.configure(text=f'{distance}')
        print(f'DISTANCE: {distance}')

        if self.general_settings_add_to_test_samples_checkbox.get() and combat_mode and distance != 0:
            self.sample_loader.add(player_cord, mark_cord, grid_gap,
                                   self.detection_color_combobox.get(),
                                   "full" if self.is_full_map else "large" if self.is_large_minimap else "small",
                                   frame=frame)

        if self.processing_show_gray_checkbox.get():
            frame = cv2.resize(grid_detector.process_frame(frame),
                               (utils.get_monitor_properties().width, utils.get_monitor_properties().height))
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        if self.processing_draw_lines_checkbox.get():
            grid_detector.draw_lines(frame)
        
        if player_cord is not None:
            cv2.circle(frame, player_cord, 15, (255, 0, 0), 5)
        if mark_cord is not None:
            cv2.circle(frame, mark_cord, 15, (0, 0, 255), 5)

        self.preview_image.set_cv2(frame)
            
        if self.general_settings_dictor_checkbox.get() and combat_mode:
            utils.text_to_speech(str(distance))

if __name__ == '__main__':
    app = App()
    app.mainloop()