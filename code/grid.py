import cv2
import numpy as np
from collections import Counter

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
        self.line_max_gap = 0
        self.canny_threshold1 = 0
        self.canny_threshold2 = 0
    
    def process_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, self.canny_threshold1,
                                self.canny_threshold2, apertureSize=3)
        return canny_frame

    def detect_lines(self, frame):
        lines = cv2.HoughLinesP(frame, 1, np.pi / 2,
                               self.line_threshold, minLineLength=self.line_min_lenth, maxLineGap=self.line_max_gap)
        if lines is None:
            self.lines = None
            return
        processed_lines = []
        for line in lines:
            line = line[0]
            processed_lines.append((int(line[0]),
                                    int(line[1]), int(line[2]), int(line[3])))

        self.lines = processed_lines
        self.merge_lines()
    
    def draw_lines(self, frame, color=(0, 255, 0)):
        if self.lines is not None:
            print("Drawing ", len(self.lines))
            for x0, y0, x1, y1 in self.lines:
                cv2.line(frame, (x0, y0), (x1, y1), color, 5)

    def hysteresis(self, a, b, hysteresis):
        if a<b+hysteresis and a>b-hysteresis:
            return True
        return False

    def merge_lines(self, threshold=30):
        merged_lines = []
        used = [False] * len(self.lines)

        for i, (x0, y0, x1, y1) in enumerate(self.lines):
            if used[i]:
                continue

            merged_x0, merged_y0, merged_x1, merged_y1 = x0, y0, x1, y1

            for j, (x2, y2, x3, y3) in enumerate(self.lines):
                if i != j and not used[j]:
                    mid1_x = (merged_x0 + merged_x1) / 2
                    mid1_y = (merged_y0 + merged_y1) / 2
                    mid2_x = (x2 + x3) / 2
                    mid2_y = (y2 + y3) / 2
                    distance = ((mid1_x - mid2_x) ** 2 + (mid1_y - mid2_y) ** 2) ** 0.5

                    if distance < threshold:
                        merged_x0 = (merged_x0 + x2) // 2
                        merged_y0 = (merged_y0 + y2) // 2
                        merged_x1 = (merged_x1 + x3) // 2
                        merged_y1 = (merged_y1 + y3) // 2
                        used[j] = True

            merged_lines.append((merged_x0, merged_y0, merged_x1, merged_y1))
            used[i] = True

        self.lines = merged_lines
    
    def mode(self, data):
        if not data:
            return None
        frequency = Counter(data)
        max_count = max(frequency.values())
        modes = [key for key, count in frequency.items() if count == max_count]
        return sum(modes) / len(modes) if len(modes) > 1 else modes[0]

    def get_grid_spaceing(self):
        horizontal_lines = []
        vertical_lines = []
        if self.lines is not None:
            for line in self.lines:
                x0, y0, x1, y1 = line
                if x0 < 10:
                    horizontal_lines.append(line)
                else: vertical_lines.append(line)
        
        horizontal_gaps = []
        vertical_gaps = []

        horizontal_lines = sorted(horizontal_lines, key=lambda x:x[1])
        vertical_lines = sorted(vertical_lines, key=lambda x:x[0])

        for i in range(0, len(horizontal_lines)-1):
            x0, y0, x1, y1 = horizontal_lines[i]
            x2, y2, x3, y3 = horizontal_lines[i+1]
            horizontal_gaps.append(y0-y2)
        
        for i in range(0, len(vertical_lines)-1):
            x0, y0, x1, y1 = vertical_lines[i]
            x2, y2, x3, y3 = vertical_lines[i+1]
            vertical_gaps.append(x0-x2)
        
        
        return (self.mode(horizontal_gaps), self.mode(vertical_gaps))
            



        
    