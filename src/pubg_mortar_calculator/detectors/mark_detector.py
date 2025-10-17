import cv2
import numpy as np

from ..utils import imgpr

class MarkDetector:
    def __init__(self) -> None:
        self.hsv_min = np.array((0, 0, 0), dtype=np.uint8)
        self.hsv_max = np.array((255, 255, 255), dtype=np.uint8)

        self.player_position = None
        self.mark_position = None

    def get_hsv_mask(self, bgr_frame:np.ndarray, color:str|None=None,
                     bluring_size: int = 19,
                     bluring_threshold: int = 15) -> np.ndarray:
        hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

        if color is not None: self.load_color(color)

        mask = cv2.inRange(hsv_frame, self.hsv_min, self.hsv_max)
        
        mask = cv2.GaussianBlur(mask, (bluring_size, bluring_size), 7)
        
        ret, mask = cv2.threshold(mask, bluring_threshold, 255, cv2.THRESH_BINARY)

        return mask

    def get_mark_positions(self, hsv_mask:np.ndarray,
                           max_radius: float) -> tuple[tuple[int, int] | None,
                                                 tuple[int, int] | None]:
        contours = self._find_contours(hsv_mask)

        player_cord = None
        mark_cord = None
        
        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            
            cx, cy = int(x), int(y)
            if radius < max_radius: 
                if player_cord == None:
                    player_cord = (cx, cy)

                elif mark_cord == None:
                    mark_cord = (cx, int(cy+(radius)))
                
                else:break

        self.player_position = player_cord
        self.mark_position = mark_cord
        return (player_cord, mark_cord)

    def load_color(self, color:str) -> tuple[np.ndarray, np.ndarray]:
        match color:
            case 'orange':
                hsv_min = (10, 106, 123)
                hsv_max = (13, 238, 231)
            case 'yellow':
                hsv_min = (23, 137, 163)
                hsv_max = (36, 255, 240)
            case 'blue':
                hsv_min = (67, 70, 106)
                hsv_max = (110, 210, 231)
            case 'green':
                hsv_min = (49, 101, 111)
                hsv_max = (80, 195, 219)
            case _:
                raise ValueError(f"There is no color {color}")
        self.hsv_min = np.array(hsv_min, dtype=np.uint8)
        self.hsv_max = np.array(hsv_max, dtype=np.uint8)
        return self.hsv_min, self.hsv_max

    def draw_marks(self, frame:np.ndarray) -> np.ndarray:
        if self.player_position is not None:
            imgpr.draw_point(frame, self.player_position, "Player", (255, 0, 0))
        if self.mark_position is not None:
            imgpr.draw_point(frame, self.mark_position, "Mark", (0, 0, 255))
        return frame

    @staticmethod
    def _find_contours(mask:np.ndarray) -> list:
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            return sorted_contours