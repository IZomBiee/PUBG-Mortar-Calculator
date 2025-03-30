import cv2
import math
import json
import numpy as np
from collections import Counter

class GridDetector:
    def __init__(self, canny_threshold1:int, canny_threshold2:int,
                 line_threshold:int,
                 max_gap:int, merge_threshold:int,
                 reference_resolution:list[int, int]=[3840, 2160]):
        self.canny_threshold1 = canny_threshold1
        self.canny_threshold2 = canny_threshold2
        self.aperture_size = 3

        self.line_threshold = line_threshold
        self.max_gap = max_gap
        self.merge_threshold = merge_threshold

        self.multiplier = [1, 1]
        self.normalize_multiplier = [1, 1]
        self.reference_resolution = reference_resolution
        self.avg_multiplier = 1

        self.vertical_lines = []
        self.horizontal_lines = []

    def process_frame(self, frame:np.ndarray) -> np.ndarray:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, self.canny_threshold1,
                                self.canny_threshold2, apertureSize=self.aperture_size)
        self.multiplier = [frame.shape[1]/self.reference_resolution[0], frame.shape[0]/self.reference_resolution[1]]
        self.avg_multiplier = sum(self.multiplier)/2
        return self.normalize_frame(canny_frame)
    
    def normalize_frame(self, frame:np.ndarray) -> np.ndarray:
        max_resolution = frame.shape[0] if frame.shape[0] > frame.shape[1] else frame.shape[1]
        self.normalize_multiplier = [frame.shape[1]/max_resolution, frame.shape[0]/max_resolution]
        frame = cv2.resize(frame, (max_resolution, max_resolution), interpolation=cv2.INTER_NEAREST)
        return frame

    def detect_lines(self, frame:np.ndarray):
        frame = self.process_frame(frame)

        lines = cv2.HoughLinesP(frame, 1, np.pi / 2,
                               int(self.line_threshold*self.avg_multiplier), maxLineGap=int(self.max_gap*self.avg_multiplier))

        if lines is None:
            lines = []
        processed_lines = []
        for line in lines:
            line = line[0]
            processed_lines.append([int(line[0]*self.normalize_multiplier[0]),
                                    int(line[1]*self.normalize_multiplier[1]),
                                    int(line[2]*self.normalize_multiplier[0]),
                                    int(line[3]*self.normalize_multiplier[1])])
        
        merged_lines = self.merge_lines(processed_lines)
        self.horizontal_lines, self.vertical_lines = self.separate_lines(merged_lines)

    def draw_lines(self, frame:np.ndarray, vertical_lines_color=(255, 0, 0), horizontal_lines_color=(0, 0, 255), trickness:int=5):
        trickness = max(int((trickness*self.avg_multiplier)), 1)
        for x0, y0, x1, y1 in self.vertical_lines:
            cv2.line(frame, (x0, y0),
                     (x1, y1), vertical_lines_color, trickness)
        
        for x0, y0, x1, y1 in self.horizontal_lines:
            cv2.line(frame, (x0, y0),
                     (x1, y1), horizontal_lines_color, trickness)

    def merge_lines(self, lines:list[int]) -> list[int]:
        merged_lines = []
        used = [False] * len(lines)

        for i, (x0, y0, x1, y1) in enumerate(lines):
            if used[i]:
                continue

            merged_x0, merged_y0, merged_x1, merged_y1 = x0, y0, x1, y1

            for j, (x2, y2, x3, y3) in enumerate(lines):
                if i != j and not used[j]:
                    mid1_x = (merged_x0 + merged_x1) / 2
                    mid1_y = (merged_y0 + merged_y1) / 2
                    mid2_x = (x2 + x3) / 2
                    mid2_y = (y2 + y3) / 2
                    distance = ((mid1_x - mid2_x) ** 2 + (mid1_y - mid2_y) ** 2) ** 0.5

                    if distance < self.merge_threshold*self.avg_multiplier:
                        merged_x0 = (merged_x0 + x2) // 2
                        merged_y0 = (merged_y0 + y2) // 2
                        merged_x1 = (merged_x1 + x3) // 2
                        merged_y1 = (merged_y1 + y3) // 2
                        used[j] = True

            merged_lines.append((merged_x0, merged_y0, merged_x1, merged_y1))
            used[i] = True

        return merged_lines
    
    def mode(self, data):
        frequency = Counter(data)
        max_count = max(frequency.values())
        modes = [key for key, count in frequency.items() if count == max_count]
        return sum(modes) / len(modes) if len(modes) > 1 else modes[0]

    def separate_lines(self, lines:list[int]) -> list[list[int], list[int]]:
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x0, y0, x1, y1 = line
            delta_x = x1-x0
            delta_y = y1-y0
            if abs(delta_x) <= 5:
                vertical_lines.append(line)
            elif abs(delta_y) <= 5:
                horizontal_lines.append(line)

        horizontal_lines = sorted(horizontal_lines, key=lambda x:x[1])
        vertical_lines = sorted(vertical_lines, key=lambda x:x[0])

        return horizontal_lines, vertical_lines

    def get_grid_gap(self) -> list[int, int]:
        horizontal_gaps = []
        vertical_gaps = []

        for i in range(0, len(self.horizontal_lines)-1):
            x0, y0, x1, y1 = self.horizontal_lines[i]
            x2, y2, x3, y3 = self.horizontal_lines[i+1]
            gap = int(abs(y0-y2))
            horizontal_gaps.append(gap)

        for i in range(0, len(self.vertical_lines)-1):
            x0, y0, x1, y1 = self.vertical_lines[i]
            x2, y2, x3, y3 = self.vertical_lines[i+1]
            gap = int(abs(x0-x2))
            vertical_gaps.append(gap)

        if len(horizontal_gaps):
            mode_horizontal_gap = int(self.mode(horizontal_gaps))
        else: mode_horizontal_gap = None
        if len(vertical_gaps):
            mode_vertical_gap = int(self.mode(vertical_gaps))
        else: mode_vertical_gap = None
        return [mode_horizontal_gap, mode_vertical_gap]

    @staticmethod
    def get_distance(first_point:list[int, int], second_point:list[int, int],
                 grid_gap:list[int, int]):
        delta_y = abs(first_point[0] - second_point[0])/grid_gap[0]*100
        delta_x = abs(first_point[1] - second_point[1])/grid_gap[1]*100
        return math.sqrt(delta_x**2+delta_y**2)

def raiseGridDetector(image:np.ndarray):
    with open('settings.json', 'r') as file:
        settings = json.load(file)

    grid_detector = GridDetector(settings["canny1_threshold"], settings["canny2_threshold"],
                                 settings["line_threshold"], settings["line_gap"], settings["merge_threshold"])

    grid_detector.detect_lines(image)
    grid_detector.draw_lines(image)

    print(f'Grid Gap: {grid_detector.get_grid_gap()}')
    cv2.imshow('Grid', cv2.resize(image, (image.shape[1]//2, image.shape[0]//2)))
    cv2.waitKey(0)

if __name__ == '__main__':
    raiseGridDetector(cv2.imread(''))