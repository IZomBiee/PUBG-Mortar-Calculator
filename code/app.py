import customtkinter
import tkinter
import numpy as np
import cv2
import tools
from PIL import Image
from grid import Grid
from profile_loader import ProfileLoader

@tools.singleton
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("PUBG-Morta-Calculator")
        # self.geometry(f"{1500}x{1500}")

        self.last_preview_path = None
        self.last_profile = None

        # Preview frame
        self.preview_frame = customtkinter.CTkFrame(self)
        self.preview_frame.grid(row=0, column=0)

        self.last_preview_image = np.zeros((512, 512, 3), dtype=np.uint8)
        self.preview_label = customtkinter.CTkLabel(self.preview_frame,
            image=customtkinter.CTkImage(Image.fromarray(self.last_preview_image),
                                         Image.fromarray(self.last_preview_image),
                                         self.last_preview_image.shape), text='')
        self.preview_label.grid(row=0, column=0)

        self.preview_grid_frame = customtkinter.CTkFrame(self.preview_frame)
        self.preview_grid_frame.grid(row=1, column=0)
        
        self.preview_grid_labeld = customtkinter.CTkLabel(self.preview_grid_frame, text='Calculated Grid Gap: ')
        self.preview_grid_labeld.grid(row=1, column=0)

        self.preview_grid_label = customtkinter.CTkLabel(self.preview_grid_frame, text='None')
        self.preview_grid_label.grid(row=1, column=1)

        self.preview_player_mark_location_labeld = customtkinter.CTkLabel(self.preview_grid_frame, text='Player Mark: ')
        self.preview_player_mark_location_labeld.grid(row=2, column=0)

        self.preview_player_mark_location_label = customtkinter.CTkLabel(self.preview_grid_frame, text='')
        self.preview_player_mark_location_label.grid(row=2, column=1)

        self.preview_player_location_labeld = customtkinter.CTkLabel(self.preview_grid_frame, text='Player: ')
        self.preview_player_location_labeld.grid(row=3, column=0)

        self.preview_player_location_label = customtkinter.CTkLabel(self.preview_grid_frame, text='')
        self.preview_player_location_label.grid(row=3, column=1)

        # Right widget
        self.right_frame = customtkinter.CTkFrame(self, fg_color='transparent')
        self.right_frame.grid(row=0, column=1)

        # Profile select frame
        self.profile_frame = customtkinter.CTkFrame(self.right_frame)
        self.profile_frame.grid(row=0, column=0)

        self.profile_label = customtkinter.CTkLabel(self.profile_frame, text="Profiles")
        self.profile_label.grid(row=0, column=1)

        self.profile_combobox = customtkinter.CTkComboBox(self.profile_frame, state="readonly", values=[], command=self.on_profile_combobox)
        self.profile_combobox.set('default')
        self.profile_combobox.grid(row=1, column=0)

        self.profile_create_button = customtkinter.CTkButton(self.profile_frame, text='Create new',
                                                             command=self.create_new_profile)
        self.profile_create_button.grid(row=1, column=1)

        self.profile_delete_button = customtkinter.CTkButton(self.profile_frame, text='Delete current',
                                                             command=self.delete_profile)
        self.profile_delete_button.grid(row=1, column=2)

        # Image Processing Frame
        self.image_frame = customtkinter.CTkFrame(self.right_frame)
        self.image_frame.grid(row=1, column=0, pady=10)
        
        self.image_label = customtkinter.CTkLabel(self.image_frame, text="Image Processing Settings")
        self.image_label.grid(row=0, column=1)

        self.image_threshold1_slider = customtkinter.CTkSlider(self.image_frame, from_=0, to=200,
                                                               command=lambda value: self.on_slider(value, self.image_threshold1_label))
        self.image_threshold1_slider.grid(row=1, column=1)
        self.image_threshold1_label = customtkinter.CTkLabel(self.image_frame,
                                                             text=int(self.image_threshold1_slider.get()))
        self.image_threshold1_label.grid(row=1, column=2)
        self.image_threshold1_labeld = customtkinter.CTkLabel(self.image_frame, text="Threshold 1")
        self.image_threshold1_labeld.grid(row=1, column=0)

        self.image_threshold2_slider = customtkinter.CTkSlider(self.image_frame, from_=0, to=200,
                                                               command=lambda value: self.on_slider(value, self.image_threshold2_label))
        self.image_threshold2_slider.grid(row=2, column=1)
        self.image_threshold2_label = customtkinter.CTkLabel(self.image_frame,
                                                             text=int(self.image_threshold2_slider.get()))
        self.image_threshold2_label.grid(row=2, column=2)
        self.image_threshold2_labeld = customtkinter.CTkLabel(self.image_frame, text="Threshold 2")
        self.image_threshold2_labeld.grid(row=2, column=0)

        self.image_line_threshold_slider = customtkinter.CTkSlider(self.image_frame, from_=0, to=3000,
                                                                   command=lambda value: self.on_slider(value, self.image_line_threshold_label))
        self.image_line_threshold_slider.grid(row=3, column=1)
        self.image_line_threshold_label = customtkinter.CTkLabel(self.image_frame,
                                                                 text=int(self.image_line_threshold_slider.get()))
        self.image_line_threshold_label.grid(row=3, column=2)
        self.image_line_threshold_labeld = customtkinter.CTkLabel(self.image_frame, text="Line Threshold")
        self.image_line_threshold_labeld.grid(row=3, column=0)

        self.image_line_min_lenth_slider = customtkinter.CTkSlider(self.image_frame, from_=0, to=3000,
                                                                   command=lambda value: self.on_slider(value, self.image_line_min_lenth_label))
        self.image_line_min_lenth_slider.grid(row=4, column=1)
        self.image_line_min_lenth_label = customtkinter.CTkLabel(self.image_frame,
                                                                 text=int(self.image_line_min_lenth_slider.get()))
        self.image_line_min_lenth_label.grid(row=4, column=2)     
        self.image_line_min_lenth_labeld = customtkinter.CTkLabel(self.image_frame, text="Line Min Lenth")
        self.image_line_min_lenth_labeld.grid(row=4, column=0)           

        self.image_line_max_gap_slider = customtkinter.CTkSlider(self.image_frame, from_=0, to=200,
                                                                 command=lambda value: self.on_slider(value, self.image_line_max_gap_label))
        self.image_line_max_gap_slider.grid(row=5, column=1)
        self.image_line_max_gap_label = customtkinter.CTkLabel(self.image_frame,
                                                               text=int(self.image_line_max_gap_slider.get()))
        self.image_line_max_gap_label.grid(row=5, column=2)  
        self.image_line_max_gap_labeld = customtkinter.CTkLabel(self.image_frame, text="Line Max Gap")
        self.image_line_max_gap_labeld.grid(row=5, column=0)   
        
        self.preview_button = customtkinter.CTkButton(self.image_frame, text='Load Example Image',
                                                      command=self.load_image_to_preview)
        self.preview_button.grid(row=6, column=1)
        self.preview_checkbox = customtkinter.CTkCheckBox(self.image_frame, text='Only lines',
                                                          command=lambda: self.calculate())
        self.preview_checkbox.grid(row=6, column=2)

        # Global Settings Frame
        self.settings_frame = customtkinter.CTkFrame(self.right_frame)
        self.settings_frame.grid(row=2, column=0)

        self.settings_label = customtkinter.CTkLabel(self.settings_frame, text='Global Settings')
        self.settings_label.grid(row=0, column=1)

        self.autoshooting_checkbox = customtkinter.CTkCheckBox(self.settings_frame, text="Autoshooting")
        self.autoshooting_checkbox.grid(row=1, column=0)

        self.dictor_checkbox = customtkinter.CTkCheckBox(self.settings_frame, text="Dictor")
        self.dictor_checkbox.grid(row=1, column=1)
        
        self.calculate_hotkey_label = customtkinter.CTkLabel(self.settings_frame, text='Hotkey:')
        self.calculate_hotkey_label.grid(row=3, column=0)

        self.calculate_hotkey_entry = customtkinter.CTkEntry(self.settings_frame)
        self.calculate_hotkey_entry.grid(row=3, column=1)

        self.calculate_button = customtkinter.CTkButton(self.settings_frame, text='Calculate', command=self.calculate)
        self.calculate_button.grid(row=3, column=2)

        # Player Frame
        self.player_frame = customtkinter.CTkFrame(self.right_frame)
        self.player_frame.grid(row=3, column=0)

        self.player_label = customtkinter.CTkLabel(self.player_frame, text='Player Color Settings')
        self.player_label.grid(row=0, column=0)
        
        self.player_color_combobox = customtkinter.CTkComboBox(self.player_frame, state="readonly",
                                                               values=['orange', 'yellow'],
                                                               command=self.on_player_color_combobox)
        self.player_color_combobox.set('')
        self.player_color_combobox.grid(row=1, column=0)

        self.player_mark_label = customtkinter.CTkLabel(self.player_frame, text='')
        self.player_mark_label.grid(row=1, column=1)

        self.player_icon_label = customtkinter.CTkLabel(self.player_frame, text='')
        self.player_icon_label.grid(row=1, column=2)

        self.load_player_color('orange')

    def on_player_color_combobox(self, value):
        self.load_player_color(value)

    def load_player_color(self, color:str):
        self.player_mark_image = cv2.imread(f'sample/player_images/{color}_mark.png')
        self.player_image = cv2.imread(f'sample/player_images/{color}_player.png')
        self.player_icon_label.configure(image=customtkinter.CTkImage(
                                        Image.fromarray(cv2.cvtColor(self.player_image, cv2.COLOR_BGR2RGB)),
                                        Image.fromarray(cv2.cvtColor(self.player_image, cv2.COLOR_BGR2RGB)),
                                        self.player_image.shape))

        self.player_mark_label.configure(image=customtkinter.CTkImage(
                                        Image.fromarray(cv2.cvtColor(self.player_mark_image, cv2.COLOR_BGR2RGB)),
                                        Image.fromarray(cv2.cvtColor(self.player_mark_image, cv2.COLOR_BGR2RGB)),
                                        self.player_mark_image.shape))

    def create_new_profile(self):
        dialog = customtkinter.CTkInputDialog(text="Write a profile name")
        entry = dialog.get_input()
        if entry != None:
            tools.combobox_add_value(self.profile_combobox, entry)
            ProfileLoader().create_new_profile(entry)
            ProfileLoader().set_profile(entry)
            self.calculate()
    
    def delete_profile(self):
        if self.profile_combobox.get() == 'default':
            tkinter.messagebox.showwarning("Warning", "You can't delete default profile")
        else:
            ProfileLoader().delete_profile(self.profile_combobox.get())
            tools.combobox_delete_value(self.profile_combobox, self.profile_combobox.get())
            ProfileLoader().set_profile(self.profile_combobox.get())
            self.calculate()
        
    def on_profile_combobox(self, value):
        ProfileLoader().set_profile(value)
        self.calculate()

    def load_image_to_preview(self, image_path:str=None):
        if image_path == None:
            image = tools.get_image_path()
        else: image = {'path':image_path } 
        self.last_preview_path = image['path']
        if image['path'] == '':return
        self.last_preview_image = cv2.imread(image['path'])
        self.calculate()
    
    def get_calculate_key(self):
        return self.calculate_hotkey_entry.get()
    
    def on_slider(self, value, slider_label_object: customtkinter.CTkLabel):
        slider_label_object.configure(text=str(int(value)))
        self.calculate()

    def draw_preview(self, frame, size=(512, 512)):
        frame = cv2.resize(frame, size)
        if len(frame.shape) == 2:
            frame = tools.cv2_to_pillow(frame, cv2.COLOR_GRAY2RGB)
        else:
            frame = tools.cv2_to_pillow(frame, cv2.COLOR_BGRA2RGB)
        frame = customtkinter.CTkImage(frame, frame, size)
        self.preview_label.configure(image=frame)
        
    def calculate(self):
        frame = self.last_preview_image.copy()
        processed_frame = Grid().process_frame(frame, self.image_threshold1_slider.get(), self.image_threshold2_slider.get())
        lines = Grid().detect_lines(processed_frame, self.image_line_min_lenth_slider.get(),
                            self.image_line_threshold_slider.get(), self.image_line_max_gap_slider.get())
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        player_position=Grid().detect_player(frame, self.player_image)
        mark_position = Grid().detect_mark(frame, self.player_mark_image)
        self.preview_player_mark_location_label.configure(text=f'{mark_position[0]} {mark_position[1]}')
        self.preview_player_location_label.configure(text=f'{player_position[0]} {player_position[1]}')
        
        if self.preview_checkbox.get():
            cv2.circle(frame,player_position, 15, (0, 255, 255), 15)
            cv2.circle(frame,mark_position, 15, (255, 0, 255), 15)
            Grid().draw_lines(frame, lines)
            self.draw_preview(frame)
        else:
            Grid().draw_lines(processed_frame, lines)
            self.draw_preview(processed_frame)

        grid_gap = Grid().get_grid_spaceing(lines)
        self.preview_grid_label.configure(text=f'{grid_gap[0]} x {grid_gap[1]}')
    
    def calculate_screen(self):
        frame = tools.take_screenshot()
        self.last_preview_image = frame
        processed_frame = Grid().process_frame(frame, self.image_threshold1_slider.get(), self.image_threshold2_slider.get())
        lines = Grid().detect_lines(processed_frame, self.image_line_min_lenth_slider.get(),
                            self.image_line_threshold_slider.get(), self.image_line_max_gap_slider.get())
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        player_position=Grid().detect_player(frame, self.player_image)
        mark_position = Grid().detect_mark(frame, self.player_mark_image)
        self.preview_player_mark_location_label.configure(text=f'{mark_position[0]} {mark_position[1]}')
        self.preview_player_location_label.configure(text=f'{player_position[0]} {player_position[1]}')
        
        if self.preview_checkbox.get():
            cv2.circle(frame,player_position, 15, (0, 255, 255), 15)
            cv2.circle(frame,mark_position, 15, (255, 0, 255), 15)
            Grid().draw_lines(frame, lines)
            self.draw_preview(frame)
        else:
            Grid().draw_lines(processed_frame, lines)
            self.draw_preview(processed_frame)

        grid_gap = Grid().get_grid_spaceing(lines)
        self.preview_grid_label.configure(text=f'{grid_gap[0]} x {grid_gap[1]}')
        distance = Grid().get_distance(player_position, mark_position)
        distance = round(distance/grid_gap[0]*100)
        if self.dictor_checkbox.get():
            tools.text_to_speech(distance)
        print(f"AN ENEMY! {distance} meters away!")
        