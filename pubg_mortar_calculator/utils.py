import pyttsx3
import cv2
import numpy as np
import pygetwindow

from tkinter import filedialog
from mss import mss
from screeninfo import get_monitors

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

def take_screenshot() -> np.ndarray:
    TITLE_BAR_PERCENT = 0.04

    windows = pygetwindow.getWindowsWithTitle("PUBG")
    if windows:
        window = windows[0]
        x, y = window.left, window.top
        w, h = window.width, window.height

        title_bar_height = int(h * TITLE_BAR_PERCENT)

        region = {
            'top': y + title_bar_height,
            'left': x,
            'width': w,
            'height': h - title_bar_height,
        }
    else:
        monitors = get_monitors()[0]
        region = {
            'top': 0,
            'left': 0,
            'width': monitors.width,
            'height': monitors.height,
        }

    with mss() as sct:
        screenshot = sct.grab(region)

    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

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