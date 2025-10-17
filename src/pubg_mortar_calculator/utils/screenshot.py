import cv2
import numpy as np
import pygetwindow

from mss import mss
from screeninfo import get_monitors

def take_game_screenshot() -> np.ndarray:
    windows = pygetwindow.getWindowsWithTitle("PUBG")
    if windows:
        window = windows[0]
        x, y = window.left, window.top
        w, h = window.width, window.height

        region = {
            'top': y,
            'left': x,
            'width': w,
            'height': h,
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