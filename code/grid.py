import cv2
import numpy as np
import time

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Grid:
    def __init__(self):
        self.lines = None
        self.line_min_lenth = 0
        self.line_threshold = 0
        self.canny_threshold1 = 0
        self.canny_threshold2 = 0
    
    def process_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, self.canny_threshold1,
                                self.canny_threshold2, apertureSize=7)
        return canny_frame

    def detect_lines(self, frame):
        lines = cv2.HoughLines(self.process_frame(frame), 1, np.pi / 2,
                               self.line_threshold)
        if lines is None:
            self.lines = None
            return
        processed_lines = []
        for line in lines:
            processed_lines.append((float(line[0][0]), float(line[0][1])))

        self.lines = processed_lines
        # self.merge_lines()
    
    def draw_lines(self, frame, color=(0, 255, 0)):
        if self.lines is not None:
            print("Drawing ", len(self.lines))
            for rho, theta in self.lines:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 400 * (-b))
                y1 = int(y0 + 400 * a)
                x2 = int(x0 - 400 * (-b))
                y2 = int(y0 - 400 * a)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 10)

    def hysteresis(self, a, b, hysteresis):
        if a<b+hysteresis and a>b-hysteresis:
            return True
        return False

    def merge_lines(self):
        merged_lines = []
        for line in self.lines:
            rho, theta = line
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            for line1 in merged_lines:
                rho1, theta1 = line1
                a = np.cos(theta1)
                b = np.sin(theta1)
                x1 = a * rho1
                y1 = b * rho1
                if self.hysteresis(x0, x1, 15) and self.hysteresis(y0, y1, 15) and line != line1:
                    merged_lines.remove(line1)
            merged_lines.append(line)
        self.lines = merged_lines
                
                    

    # def get_grid_spaceing(self):
    #     if self.lines is not None:
    #         for i in self.lines:
    #             print(i)
        
    