import pyttsx3
import cv2
import numpy as np

from tkinter import filedialog
from mss import mss
from screeninfo import get_monitors, common

def text_to_speech(text, voice_id=None, rate=150, volume=1.0):
    engine = pyttsx3.init()

    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)

    voices = engine.getProperty('voices')
    if voice_id:
        engine.setProperty('voice', voice_id)
    else:
        engine.setProperty('voice', voices[0].id)

    engine.say(str(text))
    engine.runAndWait()

def get_monitor_properties(monitor=0) -> common.Monitor:
    return get_monitors()[monitor]

def take_screenshot():
    with mss() as sct:
        frame = sct.grab((0, 0,
                            get_monitor_properties().width,
                            get_monitor_properties().height))
        frame = np.array(frame)

        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def get_image_path() -> str:
    image_path: str = filedialog.askopenfilename(title="Select a File",
                                                        filetypes=[("Image Files", "*.png;*.jpg"),
                                                                   ("PNG Files", "*.png"),
                                                                   ("JPG Files", "*.jpg")])
    return image_path

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance