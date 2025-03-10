import cv2
import numpy as np

class MarkDetector:
    def __init__(self, reference_resolution:list[int, int], max_radius:int=35):
        self.hsv_min = None
        self.hsv_max = None
        self.max_radius = max_radius
        self.multiplier = [1, 1]
        self.avg_multiplier = 1
        self.reference_resolution = reference_resolution

    def _process_image(self, frame:np.ndarray) -> np.ndarray:
        self.multiplier = [frame.shape[1]/self.reference_resolution[0], frame.shape[0]/self.reference_resolution[1]]
        self.avg_multiplier = sum(self.multiplier)/2
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv_image, tuple(self.hsv_min), tuple(self.hsv_max))
        mask[mask.shape[0]-int(400*self.avg_multiplier):mask.shape[0],
             0:int(400*self.avg_multiplier)] = np.zeros((int(400*self.avg_multiplier),
                                                         int(400*self.avg_multiplier)))
        mask = cv2.GaussianBlur(mask, (15, 15), -1)
        ret, mask = cv2.threshold(mask, 15, 255, cv2.THRESH_BINARY)
        return mask

    def _find_contours(self, mask:np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        return sorted_contours

    def get_cords(self, frame:np.ndarray, color:str=None) -> list[list[int, int]]:
        if color is not None:
            self.load_color(color)
        elif self.hsv_min is None or self.hsv_max is None:
            raise ValueError("No color")
        
        mask = self._process_image(frame)
        contours = self._find_contours(mask)

        player_cord = None
        mark_cord = None
        
        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            cx, cy = int(x), int(y)
            if radius < self.max_radius: 
                if player_cord == None:
                    player_cord = [cx, cy]

                elif mark_cord == None:
                    mark_cord = [cx, int(cy+(radius))]
                
                else:break

        return player_cord, mark_cord
    
    def draw_point(self, frame: np.ndarray, position: list[int, int], title: str, color: list = (255, 0, 0)): 
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
    

    def load_color(self, color:str):
        match color:
            case 'orange':
                self.hsv_min = [8, 106, 123]
                self.hsv_max = [17, 238, 231]
            case 'yellow':
                self.hsv_min = [19,130,130]
                self.hsv_max = [50,241,255]
            case 'blue':
                self.hsv_min = [79, 88, 129]
                self.hsv_max = [137, 224, 255]
            case 'green':
                self.hsv_min = [81,83,101]
                self.hsv_max = [155, 195, 255]

def get_minimap_frame(frame: np.ndarray, large=False) -> np.ndarray:
    h, w = frame.shape[:2]
    if large:
        safe_w = int(w * 0.26)
        safe_h = int(h * 0.465)
    else:
        safe_w = int(w * 0.16)
        safe_h = int(h * 0.28)
    return frame[h-safe_h:h, w-safe_w:w]

if __name__ == '__main__':
    mark_detector = MarkDetector([3840, 2160])
    image = cv2.imread(r"C:\Users\patri\Pictures\Screenshots\2025-03\TslGame_aPdfDhh2ZA.jpg")
    image = get_minimap_frame(image, False)
    player_cord, mark_cord = mark_detector.get_cords(image, 'yellow')
    print(player_cord, mark_cord)
    try:
        mark_detector.draw_point(image, player_cord, 'Player')
    except TypeError:pass

    try:
        mark_detector.draw_point(image, mark_cord, 'Mark')
    except TypeError:pass

    cv2.imshow('Welcome to hell', cv2.resize(image, (image.shape[1], image.shape[0])))
    cv2.waitKey(0)