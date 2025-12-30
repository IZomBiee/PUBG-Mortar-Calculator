import cv2
import os
import numpy as np
import tkinter

from src.pubg_mortar_calculator import SampleManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui.app import App

class AppLogic():
    def __init__(self, app_ui: "App"):
        self.app_ui: "App" = app_ui

        self.sample_manager = SampleManager() 
    
    def load_sample(self, index:int):
        sample = self.sample_manager[index]
        self.app_ui.map_image.set_cv2(sample.map_image)
        self.app_ui.elevation_image.set_cv2(sample.elevation_image)
        
