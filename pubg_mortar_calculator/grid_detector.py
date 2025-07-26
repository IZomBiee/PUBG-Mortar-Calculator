import cv2
import math
import json
import numpy as np

from collections import Counter
from .settings_loader import SettingsLoader as SL

class GridDetector:
    def __init__(self):
        self.multiplier = [1, 1]
        self.normalize_multiplier = [1, 1]
        self.reference_resolution = (3840, 2160)
        self.avg_multiplier = 1

        self.vertical_lines = []
        self.horizontal_lines = []

    def get_canny_frame(self, bgr_frame:np.ndarray,
                        threshold1: int,
                        threshold2: int,
                        aperture_size: int = 3) -> np.ndarray:
        gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, threshold1,
                                threshold2, apertureSize=aperture_size)
        return canny_frame

    def detect_lines(self, canny_frame:np.ndarray,
                     line_threshold: int, max_line_gap: int) -> None:
        normalized_canny_frame = self._normalize_frame(canny_frame)

        lines = cv2.HoughLinesP(normalized_canny_frame, 1, np.pi / 2,
                               int(line_threshold*self.avg_multiplier),
                               maxLineGap=int(max_line_gap*self.avg_multiplier))

        if lines is None:
            lines = []
        processed_lines = []
        for line in lines:
            line = line[0]
            processed_lines.append([int(line[0]*self.normalize_multiplier[0]),
                                    int(line[1]*self.normalize_multiplier[1]),
                                    int(line[2]*self.normalize_multiplier[0]),
                                    int(line[3]*self.normalize_multiplier[1])])
        
        self.horizontal_lines, self.vertical_lines = self._separate_lines(processed_lines)

    def draw_lines(self, frame:np.ndarray,
                   vertical_lines_color=(255, 0, 0),
                   horizontal_lines_color=(0, 0, 255),
                   trickness:int=5) -> None:
        trickness = max(int((trickness*self.avg_multiplier)), 1)
        for x0, y0, x1, y1 in self.vertical_lines:
            cv2.line(frame, (x0, y0),
                     (x1, y1), vertical_lines_color, trickness)
        
        for x0, y0, x1, y1 in self.horizontal_lines:
            cv2.line(frame, (x0, y0),
                     (x1, y1), horizontal_lines_color, trickness)
            
    def get_grid_gap(self, gap_threshold: int ) -> int | None:
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
        
        gaps = horizontal_gaps.copy()
        gaps.extend(vertical_gaps)
        gaps = list(filter(lambda gap: gap>gap_threshold, gaps))

        if len(gaps):
            mode_gap = int(self.mode(gaps))
        else: mode_gap = None
        return mode_gap
    
    def _normalize_frame(self, frame:np.ndarray) -> np.ndarray:
        max_resolution = frame.shape[0] if frame.shape[0] > frame.shape[1] else frame.shape[1]
        self.normalize_multiplier = [frame.shape[1]/max_resolution, frame.shape[0]/max_resolution]
        frame = cv2.resize(frame, (max_resolution, max_resolution), interpolation=cv2.INTER_NEAREST)
        return frame

    def _change_multipliers(self, frame:np.ndarray) -> None:
        self.multiplier = [frame.shape[1]/self.reference_resolution[0], frame.shape[0]/self.reference_resolution[1]]
        self.avg_multiplier = sum(self.multiplier)/2

    @staticmethod
    def mode(data):
        frequency = Counter(data)
        max_count = max(frequency.values())
        modes = [key for key, count in frequency.items() if count == max_count]
        return sum(modes) / len(modes) if len(modes) > 1 else modes[0]

    @staticmethod
    def _separate_lines(lines:list[int]) -> tuple[list, list]:
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

        return (horizontal_lines, vertical_lines)
        
    @staticmethod
    def get_distance(first_point:tuple[int, int], second_point:tuple[int, int],
                 grid_gap:int):
        delta_y = abs(first_point[0] - second_point[0])/grid_gap*100
        delta_x = abs(first_point[1] - second_point[1])/grid_gap*100
        return math.sqrt(delta_x**2+delta_y**2)