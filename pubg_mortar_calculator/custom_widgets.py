import tkinter
import numpy as np
import mouse
import cv2
import os 

from customtkinter import CTkSlider, CTkFrame, CTkLabel, CTkCheckBox, \
CTkComboBox, CTkImage, CTkEntry
from .settings_loader import SettingsLoader as SL
from PIL import Image

class CustomSlider:
    def __init__(self, master: CTkFrame, title:str = "Title",
                 from_:int=0, to:int=100, default:int=0, number_of_steps:int=10,
                 command=None, command_args:tuple=(), return_value=True,
                 use_settings: bool = True, **slider_args):
        self.master = master
        self.title = title
        self.command = command
        self.command_args = list(command_args)
        self.return_value = return_value
        self.use_settings = use_settings
        self.min, self.max = from_, to
        self.slider = CTkSlider(self.master, from_=from_, to=to, number_of_steps=number_of_steps, **slider_args)
        self.slider.bind("<ButtonRelease-1>", self.on_slider)
        self.label = CTkLabel(self.master, text=f'{self.slider.get()}')
        self.describe_label = CTkLabel(self.master, text=title)

        if use_settings:
            value = SL().get(title)
            if value is not None and isinstance(value, int):
                
                default = value
    
        self.set(default)
    
    def on_slider(self, _):
        value = self.get()
        self.label.configure(text=value)
        if self.use_settings:
            SL().set(self.title, value)
        if self.command is not None:
            if self.return_value:
                self.command(value, *self.command_args)
            else:
                self.command(*self.command_args)

    def grid(self, row=0, column=0, **kwargs) -> "CustomSlider":
        self.slider.grid(row=row, column=column+1, padx=(5, 5))
        self.label.grid(row=row, column=column+2, padx=(5, 15))
        self.describe_label.grid(row=row, column=column, padx=(5, 5), **kwargs)
        return self

    def set(self, value:int):
        if value > self.max: value = self.max
        elif value < self.min: value = self.min
        SL().set(self.title, value)
        self.slider.set(value)
        self.label.configure(text=str(value))
    
    def get(self) -> int:
        return int(self.slider.get())

class CustomCombobox:
    def __init__(self, master: CTkFrame, current_value:str|None=None,values:list[str]=[], state='readonly',
                 command=None, command_args:tuple=(), return_value=True, **kwargs):
        self.master = master
        self.command = command
        self.command_args = command_args
        self.return_value = return_value
        self.combobox = CTkComboBox(self.master, command=self.on_combobox,
                                                  state=state, values=list(values), **kwargs)
        if current_value is not None:
            self.add_values(current_value)
        elif len(values) > 0: self.set(values[-1])
        
    def grid(self, row=0, column=0, **kwargs) -> "CustomCombobox":
        self.combobox.grid(row=row, column=column, **kwargs)
        return self
    
    def on_combobox(self, value:str):
        if self.command is not None:
            if self.return_value:
                self.command(value, *self.command_args)
            else:
                self.command(*self.command_args)
    
    def add_values(self, values:str | list[str], select=True):
        if type(values) == str:
            values = [values]
        else:
            values = list(values)
        current_values = self.combobox.cget("values")
        current_values.extend(values)
        self.combobox.configure(values=current_values)
        if select:
            self.combobox.set(values[-1])

    def remove_value(self, value:str):
        current_values = self.combobox.cget("values")
        index = current_values.index(value)

        if index != None:
            current_values.pop(index)
        self.combobox.configure(values=current_values)
        if len(current_values) != 0:
            self.combobox.set(current_values[-1])
        else:self.combobox.set('')
    
    def set_values(self, values: str | list[str]):
        if type(values) == str:
            values = [values]
        else: values = list(values)
        self.combobox.configure(values=values)

    def set(self, value:str):
        self.combobox.set(value)
    
    def get(self) -> str:
        return self.combobox.get()

class CustomImage:
    def __init__(self, master:CTkFrame, size:tuple[int, int],
                 image_array_or_path:np.ndarray | str | None=None,
                 save_aspect_ratio: bool=False):
        self.label = CTkLabel(master, text='')
        self.size=size
        self.save_aspect_ratio = save_aspect_ratio
        if image_array_or_path is None:
            self.set_cv2(np.zeros((size[1], size[0], 3), dtype=np.uint8))
        elif type(image_array_or_path) == str:
            self.set_path(image_array_or_path)
        else:
            self.set_cv2(image_array_or_path)

    def grid(self, row=0, column=0, **kwargs) -> "CustomImage":
        self.label.grid(row=row, column=column, **kwargs)
        return self
    
    def set_path(self, path:str) -> np.ndarray | None:
        if os.path.exists(path):
            image = cv2.imread(path)
            self.set_cv2(image)
            return image
        return None

    def set_cv2(self, array) -> np.ndarray:
        self.image = array

        if self.save_aspect_ratio:
            self.resized_image = self.resize_with_aspect_ratio(self.image, self.size)
        else:
            self.resized_image = cv2.resize(self.image, self.size, interpolation=cv2.INTER_AREA)

        pillow_image = self._cv2_to_pillow(self.resized_image)
        self.label.configure(image=CTkImage(pillow_image, pillow_image, self.size))
        return self.image
        
    def _cv2_to_pillow(self, frame, cv2_color_key:int=cv2.COLOR_BGR2RGB) -> Image.Image:
        if cv2_color_key != None:
            frame = cv2.cvtColor(frame, cv2_color_key)
        return Image.fromarray(frame)

    def get_current(self) -> np.ndarray:
        return self.image
    
    def get_mouse_pos(self, real_position=False) -> None | list[int]:
        mouse_x, mouse_y = mouse.get_position()

        widget_x = self.label.winfo_rootx()
        widget_y = self.label.winfo_rooty()
        widget_width = self.label.winfo_width()
        widget_height = self.label.winfo_height()

        relative_x = mouse_x - widget_x
        relative_y = mouse_y - widget_y

        if relative_x > widget_width or relative_y > widget_height:
            return None
        elif relative_x < 0 or relative_y < 0:
            return None
        else:
            if not real_position:
                image_width = self.image.shape[1]
                image_height = self.image.shape[0]

                scale_x = image_width / widget_width
                scale_y = image_height / widget_height

                scaled_x = int(relative_x * scale_x)
                scaled_y = int(relative_y * scale_y)
                return [scaled_x, scaled_y]
            else:
                return [relative_x, relative_y]

    @staticmethod
    def resize_with_aspect_ratio(image: np.ndarray, output_size: tuple[int, int]) -> np.ndarray:
        original_height, original_width = image.shape[:2]
        target_width, target_height = output_size

        original_aspect = original_width / original_height
        target_aspect = target_width / target_height
        if original_aspect > target_aspect:
            new_width = target_width
            new_height = int(target_width / original_aspect)
        else:
            new_height = target_height
            new_width = int(target_height * original_aspect)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        result[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image
        return result

class CustomEntry:
    def __init__(self, master:CTkFrame, text:str='',
                 placeholder_text:str='Description', state:str='normal',
                 use_settings:bool=True, **kwargs):
        self.placeholder_text = placeholder_text
        self.text_varible = tkinter.StringVar()
        self.text_varible.set(text)
        self.use_settings = use_settings
        self.entry = CTkEntry(master, textvariable=self.text_varible,
                              placeholder_text=placeholder_text, state=state, **kwargs)
        self.entry.bind("<FocusOut>", self.on_entry)
        
        if self.use_settings:
            value = SL().get(placeholder_text)
            if value is not None and isinstance(value, str):
                self.set(value)

    def on_entry(self, _):
        print(self.placeholder_text, self.get())
        SL().set(self.placeholder_text, self.get())

    def get(self):
        return self.entry.get()
    
    def set(self, text:str):
        self.text_varible.set(text)
    
    def configure(self, **kwargs):
        self.entry.configure(**kwargs)
    
    def grid(self, row:int=0, column:int=0, **kwargs) -> "CustomEntry":
        self.entry.grid(row=row, column=column, **kwargs)
        return self

class CustomCheckbox:
    def __init__(self, master:CTkFrame, text:str = 'Text', default:bool=False,
                 command=None, command_args:tuple=(),
                 use_settings: bool = True, **checkbox_args):
        self.master = master
        self.text = text
        self.command = command
        self.command_args = list(command_args)
        self.use_settings = use_settings
        self.checkbox = CTkCheckBox(self.master, text=text, command=self.on_checkbox, **checkbox_args)

        if use_settings:
            value = SL().get(text)
            if value is not None and isinstance(value, bool):
                default = value
    
        self.set(default)
    
    def on_checkbox(self):
        if self.use_settings:
            SL().set(self.text, self.get())
        if self.command is not None:
            self.command(*self.command_args)

    def grid(self, row=0, column=0, **kwargs) -> "CustomCheckbox":
        self.checkbox.grid(row=row, column=column, **kwargs)
        return self
    
    def set(self, value:bool):
        SL().set(self.text, value)
        if value: self.checkbox.select()
        else: self.checkbox.deselect()
    
    def get(self) -> bool:
        return bool(self.checkbox.get())