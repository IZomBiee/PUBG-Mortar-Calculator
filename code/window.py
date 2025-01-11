from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPixmap, QImage
import numpy as np
import cv2
from mss import mss
from screeninfo import get_monitors
from grid import Grid

class Window(QMainWindow):
    def __init__(self, path):
        super().__init__()
        uic.loadUi(path, self)
    
    def is_autoshoting(self):
        return self.AutoShootingCheckbox.isChecked()
    
    def is_distance_voicing(self):
        return self.DistanceVoicingCheckbox.isChecked()
    
    def get_monitor_size(self, monitor=0):
        return get_monitors()[monitor]

    def draw_preview(self, frame):
        frame = cv2.resize(frame, (200, 200))
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

        self.PreviewImageLabel.setPixmap(QPixmap(
                QImage(frame,
                       frame.shape[1],
                       frame.shape[0],
                       frame.strides[0],
                       QImage.Format.Format_RGB888)
                ))
    
    def take_screenshot(self):
        with mss() as sct:
            frame = sct.grab((0, 0,
                              self.get_monitor_size().width,
                              self.get_monitor_size().height))
            frame = np.array(frame)
            self.last_frame = frame
            return frame

    def sample_card(self):
        print("Getting screen...")
        self.last_frame = cv2.imread(r"C:\Users\patri\Pictures\Screenshots\2025-01\TslGame_uN9BkO6oZl.jpg")
        Grid().line_threshold = self.LineThresholdSlider.value()
        Grid().line_min_lenth = self.MinLineLenthSlider.value()
        Grid().canny_threshold1 = self.Threshold1Slider.value()
        Grid().canny_threshold2 = self.Threshold2Slider.value()
        Grid().detect_lines(self.last_frame)
        # Grid().detect_lines(self.take_screenshot())
        Grid().draw_lines(self.last_frame)
        self.draw_preview(self.last_frame)


    def calculate(self):
        print("Doing fire!")

    def setup_buttons(self):
        self.SampleCardButton.clicked.connect(self.sample_card)
        self.CalculateButton.clicked.connect(self.calculate)

        