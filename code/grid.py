import cv2
import numpy as np
from collections import Counter
import tools


@tools.singleton
class Grid:  
    def process_frame(self, frame, threshold1, threshold2):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(gray_frame, threshold1,
                                threshold2, apertureSize=3)
        return canny_frame

    def detect_lines(self, frame, min_lenth, threshold, max_gap):
        lines = cv2.HoughLinesP(frame, 1, np.pi / 2,
                               int(threshold), minLineLength=int(min_lenth), maxLineGap=int(max_gap))
        if lines is None:
            return
        processed_lines = []
        for line in lines:
            line = line[0]
            processed_lines.append((int(line[0]),
                                    int(line[1]), int(line[2]), int(line[3])))
        return self.merge_lines(processed_lines)
    
    def match_template(self, frame, template):
        if len(frame.shape) == 3:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame_gray = frame

        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
            
        result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_loc
    
    def detect_player(self, frame,):
        ...
    
    def draw_lines(self, frame, lines, color=(0, 255, 0), trickness=5):
        if lines is not None:
            for x0, y0, x1, y1 in lines:
                cv2.line(frame, (x0, y0), (x1, y1), color, trickness)

    def merge_lines(self, lines, threshold=30):
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

                    if distance < threshold:
                        merged_x0 = (merged_x0 + x2) // 2
                        merged_y0 = (merged_y0 + y2) // 2
                        merged_x1 = (merged_x1 + x3) // 2
                        merged_y1 = (merged_y1 + y3) // 2
                        used[j] = True

            merged_lines.append((merged_x0, merged_y0, merged_x1, merged_y1))
            used[i] = True

        return merged_lines
    
    def mode(self, data):
        if not data:
            return None
        frequency = Counter(data)
        max_count = max(frequency.values())
        modes = [key for key, count in frequency.items() if count == max_count]
        return sum(modes) / len(modes) if len(modes) > 1 else modes[0]

    def get_grid_spaceing(self, lines):
        horizontal_lines = []
        vertical_lines = []
        if lines is not None:
            for line in lines:
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
            



        
    