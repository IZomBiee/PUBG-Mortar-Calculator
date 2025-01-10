import cv2
import numpy as np

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Grid:
    def __init__(self, min_lenth, canny_threshold1, canny_threshold2):
        self.lines = None
        self.min_lenth = min_lenth
        self.canny_threshold1 = canny_threshold1
        self.canny_threshold2 = canny_threshold2
    
    def process_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, self.canny_threshold1,
                                self.canny_threshold2, apertureSize=7)
        return canny_frame

    def detect_lines(self, frame):
        lines = cv2.HoughLinesP(self.process_frame(frame), 1, np.pi / 180, self.min_lenth)
        self.lines = lines
    
    def draw_lines(self, frame, color=(0, 255, 0)):
        if self.lines is not None:
            for line in self.lines:
                x0, y0, x1, y1 = line[0]
                cv2.line(frame, (x0, y0), (x1, y1), color, 5)
    
    def get_grid_spaceing(self):
        if self.lines is not None:
            for i in self.lines:
                print(i)
        
    