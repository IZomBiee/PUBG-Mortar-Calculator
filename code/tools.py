import cv2
import tkinter
import os
import json
import numpy as np
from mss import mss
from screeninfo import get_monitors, common
from PIL import Image

def cv2_to_pillow(frame, cv2_color_key:int=None) -> Image:
    if cv2_color_key != None:
        frame = cv2.cvtColor(frame, cv2_color_key)
    return Image.fromarray(frame)

def get_monitor_properties(monitor=0) -> common.Monitor:
    return get_monitors()[monitor]

def take_screenshot(self):
    with mss() as sct:
        frame = sct.grab((0, 0,
                            self.get_monitor_size().width,
                            self.get_monitor_size().height))
        frame = np.array(frame)
        return frame

def get_image_path() -> dict:
    image_path: str = tkinter.filedialog.askopenfilename(title="Select a File",
                                                        filetypes=[("Image Files", "*.png;*.jpg"),
                                                                   ("PNG Files", "*.png"),
                                                                   ("JPG Files", "*.jpg")])
    image_name = image_path.split('/')[-1]
    image_format = '.'+image_name.split('.')[-1]
    return {'name':image_name, 'path':image_path, 'format':image_format}

def combobox_add_value(combobox, value):
    current_values = combobox.cget("values")
    current_values.append(value)
    combobox.configure(values=current_values)
    combobox.set(value)

def combobox_delete_value(combobox, value):
    current_values = combobox.cget("values")
    try:
        index = current_values.index(value)
    except ValueError:return
    else:
        if index != None:
            current_values.pop(index)
        combobox.configure(values=current_values)
        if len(current_values) != 0:
            combobox.set(current_values[-1])
        else:combobox.set('')

def list_profiles() -> list[dict]:
    profiles = []
    for file in os.listdir(r'sample/profiles'):
        if file.endswith('.json'):
            with open(f'sample/profiles/{file}', 'r') as file:
                profiles.append(json.load(file))

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance
