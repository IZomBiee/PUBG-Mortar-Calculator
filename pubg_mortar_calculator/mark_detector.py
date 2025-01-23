import cv2
import numpy as np

class MarkDetector:
    def __init__(self, color:str, max_radius:int):
        self.load_color(color)
        self.max_radius = max_radius
        self.cords = []

    def _process_image(self, frame:np.ndarray) -> np.ndarray:
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv_image, tuple(self.hsv_min), tuple(self.hsv_max))
        mask[mask.shape[0]-400:mask.shape[0], 0:400] = np.zeros((400, 400))
        mask = cv2.GaussianBlur(mask, (41, 41), -1)
        ret, mask = cv2.threshold(mask, 15, 255, cv2.THRESH_BINARY)
        return mask

    def _find_contours(self, mask:np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        thresholded_contours = []
        for contour in sorted_contours:
            thresholded_contours.append(contour)
        return thresholded_contours

    def get_cords(self, frame:np.ndarray) -> list[list[int, int]]:
        mask = self._process_image(frame)
        contours = self._find_contours(mask)

        player_cord = [None, None]
        mark_cord = [None, None]

        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            cx, cy = int(x), int(y)
            if radius < self.max_radius: 
                if player_cord[0] == None:
                    player_cord = [cx, cy]

                elif mark_cord[0] == None:
                    mark_cord = [cx, int(cy+(radius))]
                
                else:break

        return player_cord, mark_cord

    def load_color(self, color:str):
        match color:
            case 'orange':
                self.hsv_min = [8, 111, 138]
                self.hsv_max = [14, 254, 245]
            case 'yellow':
                self.hsv_min = [29,130,130]
                self.hsv_max = [50,241,255]
            case 'blue':
                self.hsv_min = [34, 50, 149]
                self.hsv_max = [144, 227, 245]
            case 'green':
                self.hsv_min = [81,83,101]
                self.hsv_max = [155, 195, 255]

if __name__ == '__main__':
    mark_detector = MarkDetector('yellow', 35)
    image = cv2.imread(r"tests/test_samples/TslGame_UjKKW8qwOo.jpg")
    player_cord, mark_cord = mark_detector.get_cords(image)
    # image = cv2.cvtColor(mark_detector._process_image(image), cv2.COLOR_GRAY2BGR)
    cv2.circle(image, player_cord, 5, (0, 0, 255), 5)
    cv2.circle(image, mark_cord, 5, (255, 0, 0), 5)
    cv2.imshow('Welcome to hell', cv2.resize(image, (1000, 1000)))
    cv2.waitKey(0)