import cv2
import numpy as np

class MarkDetector:
    def __init__(self) -> None:
        self.hsv_min = np.array((0, 0, 0), dtype=np.uint8)
        self.hsv_max = np.array((255, 255, 255), dtype=np.uint8)

        self.player_position = None
        self.mark_position = None

    def get_hsv_mask(self, bgr_frame:np.ndarray, color:str|None=None,
                     bluring_size: int = 19,
                     bluring_threshold: int = 15, cut_borders:bool=True) -> np.ndarray:
        hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

        if color is not None: self.load_color(color)

        mask = cv2.inRange(hsv_frame, self.hsv_min, self.hsv_max)

        if cut_borders:
            mask = self.replace_area_with_black(mask, (0, mask.shape[0]-350),
                                        (550, mask.shape[0]))

            mask = self.replace_area_with_black(mask, (mask.shape[1]-900, 0),
                                                    (mask.shape[1], 400))
        
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
        print(f"LOAD {color}")
        match color:
            case 'orange':
                hsv_min = (10, 106, 123)
                hsv_max = (13, 238, 231)
            case 'yellow':
                hsv_min = (22, 79, 99)
                hsv_max = (50, 255, 255)
            case 'blue':
                hsv_min = (67, 70, 106)
                hsv_max = (110, 210, 231)
            case 'green':
                hsv_min = (49, 101, 154)
                hsv_max = (80, 195, 218)
            case _:
                raise ValueError(f"There is no color {color}")
        self.hsv_min = np.array(hsv_min, dtype=np.uint8)
        self.hsv_max = np.array(hsv_max, dtype=np.uint8)
        return self.hsv_min, self.hsv_max

    def draw_marks(self, frame:np.ndarray) -> np.ndarray:
        if self.player_position is not None:
            self.draw_point(frame, self.player_position, "Player", (255, 0, 0))
        if self.mark_position is not None:
            self.draw_point(frame, self.mark_position, "Mark", (0, 0, 255))
        return frame

    @staticmethod
    def _find_contours(mask:np.ndarray) -> list:
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            return sorted_contours

    @staticmethod
    def draw_point(frame: np.ndarray,
                   position: tuple[int, int],
                   title: str,
                   color: tuple = (255, 0, 0), radius: int = 40,
                   thickness:int = 12, font_scale:int=3): 
        cv2.circle(frame, position, radius, color, thickness)

        font_thickness = max(1, int(font_scale * 3))

        text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX,
                                    font_scale, font_thickness)[0]
        text_w, text_h = text_size

        bg_x, bg_y = position[0] - text_w // 2, position[1] - text_h - 10
        bg_x = max(0, min(bg_x, frame.shape[1] - text_w))
        bg_y = max(text_h + 10, min(bg_y, frame.shape[0] - 10))

        cv2.rectangle(frame, (bg_x - 5, bg_y - text_h - 5),
                      (bg_x + text_w + 5, bg_y + 5), (0, 0, 0), -1)
        cv2.putText(frame, title, (bg_x, bg_y), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, (255, 255, 255), font_thickness)

    @staticmethod
    def replace_area_with_black(image: np.ndarray,
                                point1: tuple[int, int],
                                point2: tuple[int, int]):
        x1, y1 = point1
        x2, y2 = point2

        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if len(image.shape) == 3:
            image[int(y1):int(y2), int(x1):int(x2)] = (0, 0, 0)
        else:
            image[int(y1):int(y2), int(x1):int(x2)] = 0
        
        return image