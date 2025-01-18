import customtkinter
import numpy as np
import cv2
from PIL import Image

class CustomSlider:
    def __init__(self, master: customtkinter.CTkFrame, title:str='Title', from_:int=0, to:int=100, number_of_steps:int=10,
                 command=None, command_args:tuple=(), return_value=True):
        self.master = master
        self.command = command
        self.command_args = list(command_args)
        self.return_value = return_value
        self.slider = customtkinter.CTkSlider(self.master, from_=from_, to=to, number_of_steps=number_of_steps, command=self.on_slider)
        self.label = customtkinter.CTkLabel(self.master, text=int(self.slider.get()))
        self.describe_label = customtkinter.CTkLabel(self.master, text=title)
    
    def on_slider(self, value):
        value = int(value)
        self.label.configure(text=value)
        if self.command is not None:
            if self.return_value:
                self.command(value, *self.command_args)
            else:
                self.command(*self.command_args)

    def grid(self, row=0, column=0):
        self.slider.grid(row=row, column=column+1)
        self.label.grid(row=row, column=column+2)
        self.describe_label.grid(row=row, column=column)
    
    def set(self, value:int):
        self.slider.set(value)
        self.label.configure(text=str(value))
    
    def get(self) -> int:
        return int(self.slider.get())

class CustomCombobox:
    def __init__(self, master: customtkinter.CTkFrame, current_value:str=None,values:list[str]=[], state='readonly',
                 command=None, command_args:tuple=()):
        self.master = master
        self.command = command
        self.command_args = command_args
        self.combobox = customtkinter.CTkComboBox(self.master, command=self.on_combobox, state=state, values=list(values))
        if current_value is not None:
            self.add_value(current_value)
        
    
    def grid(self, row=0, column=0):
        self.combobox.grid(row=row, column=column)
    
    def on_combobox(self, value:str):
        if self.command is not None:
            self.command(value, *self.command_args)
    
    def add_values(self, values:str | list[str], select=True):
        if type(values) == str:
            values = [values]
        else: values = list[values]
        current_values = self.combobox.cget("values")
        current_values.extend(values)
        self.combobox.configure(values=current_values)
        if select:
            self.combobox.set(values)

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
    def __init__(self, master:customtkinter.CTkFrame, size:tuple[int], image_array_or_path:np.ndarray | str=None):
        self.label = customtkinter.CTkLabel(master, text='')
        self.size=size
        if image_array_or_path is None:
            self.set_cv2(np.zeros((size[0], size[1], 3), dtype=np.uint8))
        elif type(image_array_or_path) == str:
            self.set_path(image_array_or_path)
        else:
            self.set_cv2(image_array_or_path)

    def grid(self, row=0, column=0):
        self.label.grid(row=row, column=column)

    def set_path(self, path:str) -> np.ndarray:
        image = cv2.imread(path)
        self.set_cv2(image)
        return image

    def set_cv2(self, array) -> np.ndarray:
        self.image = array
        self.image = cv2.resize(self.image, self.size, interpolation=cv2.INTER_AREA)

        self.label.configure(image=customtkinter.CTkImage(None, self._cv2_to_pillow(self.image), self.size))
        return self.image
        
    def _cv2_to_pillow(self, frame, cv2_color_key:int=cv2.COLOR_BGR2RGB) -> Image:
        if cv2_color_key != None:
            frame = cv2.cvtColor(frame, cv2_color_key)
        return Image.fromarray(frame)

    def get_current(self) -> np.ndarray:
        return self.image