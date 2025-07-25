import cv2
import numpy as np

class MarkDetector:
    def __init__(self, reference_resolution:tuple[int, int], max_radius:int=35):
        self.hsv_min = np.array((0, 0, 0), dtype=np.uint8)
        self.hsv_max = np.array((255, 255, 255), dtype=np.uint8)
        self.max_radius = max_radius
        self.multiplier = [1, 1]
        self.avg_multiplier = 1
        self.reference_resolution = reference_resolution

    def _process_image(self, frame:np.ndarray) -> np.ndarray:
        self.multiplier = [frame.shape[1]/self.reference_resolution[0], frame.shape[0]/self.reference_resolution[1]]
        self.avg_multiplier = sum(self.multiplier)/2
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv_image, self.hsv_min, self.hsv_max)

        mask = self.replace_area_with_black(mask, (0, mask.shape[0]-(350*self.avg_multiplier)),
                                      (550*self.avg_multiplier, mask.shape[0]))

        mask = self.replace_area_with_black(mask, (mask.shape[1]-(900*self.avg_multiplier), 0),
                                                (mask.shape[1], 400*self.avg_multiplier))

        mask = cv2.GaussianBlur(mask, (19, 19), 7)
        ret, mask = cv2.threshold(mask, 15, 255, cv2.THRESH_BINARY)
        return mask

    def _find_contours(self, mask:np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        return sorted_contours

    def get_cords(self, frame:np.ndarray, color:str|None=None) -> tuple[tuple[int, int] | None,
                                                                   tuple[int, int] | None]:
        if color is not None:
            self.load_color(color)
        
        mask = self._process_image(frame)
        contours = self._find_contours(mask)

        player_cord = None
        mark_cord = None
        
        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour)

            cx, cy = int(x), int(y)
            if radius < self.max_radius: 
                if player_cord == None:
                    player_cord = (cx, cy)

                elif mark_cord == None:
                    mark_cord = (cx, int(cy+(radius)))
                
                else:break

        return (player_cord, mark_cord)
    
    def draw_point(self, frame: np.ndarray, position: tuple[int, int], title: str, color: tuple = (255, 0, 0)): 
        radius = int(40*self.avg_multiplier)
        thickness = int(12*self.avg_multiplier)

        cv2.circle(frame, position, radius, color, thickness)

        font_scale = 3*self.avg_multiplier
        font_thickness = max(1, int(font_scale * 3))

        text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        text_w, text_h = text_size

        bg_x, bg_y = position[0] - text_w // 2, position[1] - text_h - 10
        bg_x = max(0, min(bg_x, frame.shape[1] - text_w))
        bg_y = max(text_h + 10, min(bg_y, frame.shape[0] - 10))

        cv2.rectangle(frame, (bg_x - 5, bg_y - text_h - 5), (bg_x + text_w + 5, bg_y + 5), (0, 0, 0), -1)
        cv2.putText(frame, title, (bg_x, bg_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
    
    @staticmethod
    def replace_area_with_black(image, point1, point2):
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

    def load_color(self, color:str):
        match color:
            case 'orange':
                hsv_min = (10, 106, 123)
                hsv_max = (13, 238, 231)
            case 'yellow':
                hsv_min = (25,130,130)
                hsv_max = (50,241,255)
            case 'blue':
                hsv_min = (67, 70, 106)
                hsv_max = (110, 210, 231)
            case 'green':
                hsv_min = (81,83,101)
                hsv_max = (155, 195, 255)
            case _:
                raise ValueError(f"There is no color {color}")
        self.hsv_min = np.array(hsv_min, dtype=np.uint8)
        self.hsv_max = np.array(hsv_max, dtype=np.uint8)

def raiseMarkDetector(image: np.ndarray, color:str):
    mark_detector = MarkDetector((3840, 2160))

    player_cord, mark_cord = mark_detector.get_cords(image, color)
    print(f"Player Position: {player_cord} Mark Position: {mark_cord}")

    image = cv2.bitwise_and(cv2.cvtColor(mark_detector._process_image(image), cv2.COLOR_GRAY2BGR), image)
    if player_cord is not None:
        mark_detector.draw_point(image, player_cord, 'Player')
    if mark_cord is not None:
        mark_detector.draw_point(image, mark_cord, 'Mark', (0, 0, 255))

    cv2.imshow('Grid', cv2.resize(image,(image.shape[1]//2, image.shape[0]//2)))
    cv2.waitKey(0)

if __name__ == '__main__':
    raiseMarkDetector(cv2.imread(
        r"D:/Projects/Python/PUBG-Mortar-Calculator/tests/test_samples/2025-04-17_18-18-20.png"
        ), "blue")
    