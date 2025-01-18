import customtkinter
import tkinter
import numpy as np
import cv2
import tools
from PIL import Image
from grid import Grid
from custom_widgets import *

from settings_loader import SettingsLoader
from profile_loader import ProfileLoader

@tools.singleton
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("PUBG-Morta-Calculator")
        self.geometry(f"{1500}x{1500}")

        self.last_preview_path = None
        self.last_image = None
        self.player_image = None
        self.mark_image = None


        # Preview Frame
        self.preview_frame = customtkinter.CTkFrame(self)
        self.preview_frame.grid(row=0, column=0)

        self.preview_image = CustomImage(self.preview_frame, (512, 512))
        self.preview_image.grid(row=0, column=0)

        # Calculation Frame 
        self.calculation_frame = customtkinter.CTkFrame(self.preview_frame)
        self.calculation_frame.grid(row=1, column=0)
        
        self.calculation_title_label = customtkinter.CTkLabel(self.calculation_frame, text='Calculated values')
        self.calculation_title_label.grid(row=1, column=0)

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

        # Profile Frame
        self.profile_frame = customtkinter.CTkFrame(self.right_frame)
        self.profile_frame.grid(row=0, column=0)

        self.profile_title_label = customtkinter.CTkLabel(self.profile_frame, text="Profiles")
        self.profile_title_label.grid(row=0, column=1)

        self.profile_combobox = CustomCombobox(self.profile_frame, values=[], command=self.on_profile_combobox)
        self.profile_combobox.grid(row=1, column=0)


        self.profile_create_button = customtkinter.CTkButton(self.profile_frame, text='Create new', command=self.create_new_profile)
        self.profile_create_button.grid(row=1, column=1)

        self.profile_delete_button = customtkinter.CTkButton(self.profile_frame, text='Delete current', command=self.delete_profile)
        self.profile_delete_button.grid(row=1, column=2)

        # Processing Frame
        self.processing_frame = customtkinter.CTkFrame(self.right_frame)
        self.processing_frame.grid(row=1, column=0, pady=10)
        
        self.processing_title_label = customtkinter.CTkLabel(self.processing_frame, text="Image Processing Settings")
        self.processing_title_label.grid(row=0, column=1)

        self.processing_threshold1_slider = CustomSlider(self.processing_frame, 'Threshold 1', 0, 200,
                                                         command=self.process_preview_image, return_value=False)
        self.processing_threshold1_slider.grid(1, 0)

        self.processing_threshold2_slider = CustomSlider(self.processing_frame, 'Threshold 2', 0, 200,
                                                         command=self.process_preview_image, return_value=False)
        self.processing_threshold2_slider.grid(2, 0)

        self.processing_line_threshold_slider = CustomSlider(self.processing_frame, 'Line Threshold', 0, 2000,
                                                             command=self.process_preview_image, return_value=False)
        self.processing_line_threshold_slider.grid(3, 0)

        self.processing_line_min_lenth_slider = CustomSlider(self.processing_frame, 'Line Min. Lenth', 0, 4000,
                                                             command=self.process_preview_image, return_value=False)
        self.processing_line_min_lenth_slider.grid(4, 0)

        self.processing_max_gap_slider = CustomSlider(self.processing_frame, 'Max. Gap', 0, 500,
                                                      command=self.process_preview_image, return_value=False)
        self.processing_max_gap_slider.grid(5, 0)
   
        self.processing_load_example_button = customtkinter.CTkButton(self.processing_frame, text='Load Example Image',
                                                      command=self.on_preview_image_load)
        self.processing_load_example_button.grid(row=6, column=1)

        self.processing_only_lines_checkbox = customtkinter.CTkCheckBox(self.processing_frame, text='Only lines',
                                                          command=self.process_preview_image)
        self.processing_only_lines_checkbox.grid(row=6, column=2)

        # General Settings Frame
        self.general_settings_frame = customtkinter.CTkFrame(self.right_frame)
        self.general_settings_frame.grid(row=2, column=0)

        self.general_settings_title_label = customtkinter.CTkLabel(self.general_settings_frame, text='General Settings')
        self.general_settings_title_label.grid(row=0, column=1)

        self.general_settings_autoshooting_checkbox = customtkinter.CTkCheckBox(self.general_settings_frame, text="Autoshooting")
        self.general_settings_autoshooting_checkbox.grid(row=1, column=0)

        self.general_settings_dictor_checkbox = customtkinter.CTkCheckBox(self.general_settings_frame, text="Dictor")
        self.general_settings_dictor_checkbox.grid(row=1, column=1)
        
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
                                                       command=self.on_detection_color_combobox)
        self.detection_color_combobox.grid(row=1, column=0)

        self.detection_mark_image = CustomImage(self.detection_frame, (52, 52))
        self.detection_mark_image.grid(row=1, column=1)

        self.detection_player_image = CustomImage(self.detection_frame, (52, 52))
        self.detection_player_image.grid(row=1, column=2)
    
    def on_preview_image_load(self, path:str=None):
        if path is None:
            path = tools.get_image_path()
            if path == '':
                return
            else: self.last_preview_path = path
        else: self.last_preview_path = path
        if self.last_preview_path is not None:
            self.last_image = self.preview_image.set_path(self.last_preview_path)
            self.process_preview_image()

    def on_detection_color_combobox(self, value):
        self.load_player_color(value)
        self.process_preview_image()

    def load_player_color(self, color:str):
        self.mark_image = cv2.imread(f'sample/player_images/{color}_mark.png')
        self.player_image = cv2.imread(f'sample/player_images/{color}_player.png')
        
        self.detection_player_image.set_cv2(self.player_image)
        self.detection_mark_image.set_cv2(self.mark_image)

        self.process_preview_image()

    def create_new_profile(self):
        dialog = customtkinter.CTkInputDialog(text="Write a profile name")
        entry = dialog.get_input()
        if entry != None:
            ProfileLoader().create_profile(entry)

    def delete_profile(self):
        if self.profile_combobox.get() == 'default':
            tkinter.messagebox.showwarning("Warning", "You can't delete default profile")
        else:
            ProfileLoader().delete_profile(self.profile_combobox.get())
        
    def on_profile_combobox(self, value):
        ProfileLoader().change_profile(value)

    def get_calculate_key(self):
        return self.general_settings_hotkey_entry.get()
    
    def process_preview_image(self, combat_mode=False):
        if combat_mode:
            self.last_image = tools.take_screenshot()
        else:
            if self.last_image is None: return
        image = self.last_image.copy()
        processed_image = Grid().process_frame(image, self.processing_threshold1_slider.get(), self.processing_threshold2_slider.get())
        lines = Grid().detect_lines(processed_image, self.processing_line_min_lenth_slider.get(), self.processing_line_threshold_slider.get(),
                                    self.processing_max_gap_slider.get())
        lines = Grid().merge_lines(lines, 30)

        if self.player_image is not None:
            player_position = Grid().detect_player(image, self.player_image)
        else: player_position = None
        if self.mark_image is not None:
            mark_position = Grid().detect_mark(image, self.mark_image)
        else: mark_position = None

        processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
        if not self.processing_only_lines_checkbox.get():
            image = processed_image

        Grid().draw_lines(image, lines)
        if mark_position is not None:
            cv2.circle(image,player_position, 15, (0, 255, 255), 15)
            self.calculation_mark_cordinates_label.configure(text=f'{mark_position}')
        if player_position is not None:
            cv2.circle(image,mark_position, 15, (255, 0, 255), 15)
            self.calculation_player_cordinates_label.configure(text=f'{player_position}')

        grid_gap = Grid().get_grid_spaceing(lines)
        if mark_position is not None and player_position is not None and not None in grid_gap:
            distance = round(Grid().get_distance(mark_position, player_position)/grid_gap[0]*100)

        else: distance = None

        if self.general_settings_dictor_checkbox.get() and combat_mode:
            tools.text_to_speech(distance)

        self.calculation_grid_gap_label.configure(text=f'{grid_gap}')
        
        if distance is not None:
            self.calculation_distance_label.configure(text=f'{distance}')
        self.preview_image.set_cv2(image)
        