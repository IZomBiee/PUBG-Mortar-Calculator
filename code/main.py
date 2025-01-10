import cv2
import keyboard
import numpy as np
from grid import Grid
from PyQt6.QtWidgets import QApplication
from window import Window
import sys

grid = Grid(1000, 100, 100)

while True:
    app = QApplication(sys.argv)
    window = Window('main.ui')
    window.setup_buttons()
    window.show()
    app.exec()

    # frame = cv2.imread(r"C:\Users\patri\Pictures\Screenshots\2025-01\TslGame_WvdkKjAjRf.jpg")
    # grid.detect_lines(frame)
    # grid.draw_lines(frame)
    # grid.get_grid_spaceing()



    # frame = cv2.resize(frame, (1000, 1000))
    # cv2.imshow('Hello Darkness', grid.process_frame(frame))
    # cv2.waitKey(100)


            
    

