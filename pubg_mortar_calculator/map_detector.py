import cv2
import numpy as np

class MapDetector:
    def __init__(self, reference_resolution:list[int, int]):
        self.reference_resolution = reference_resolution
        self.multiplier = [None, None]
        self.minimap_boundarys = [3200, 1500, 3839, 2139]
        self.clock_radious = 22.77

    def is_minimap(self, frame: np.ndarray) -> bool:
        minimap_frame = self.get_minimap_image(frame)
        minimap_gray_frame = cv2.cvtColor(minimap_frame, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(minimap_gray_frame, 230, 255, cv2.THRESH_BINARY)

        contours = self._find_contours(mask)
        
        (x, y), radius = cv2.minEnclosingCircle(contours[1])
        if self.clock_radious-0.3 < radius*max(self.multiplier) or radius*max(self.multiplier) > self.clock_radious+0.3:
            return False
        else: return True

    def get_minimap_bounderies(self, frame: np.ndarray) -> list[int]:
        self.multiplier = [frame.shape[1]/
                           self.reference_resolution[0],
                           frame.shape[0]/
                           self.reference_resolution[1]]
        return [round(3260*self.multiplier[0]), round(1580*self.multiplier[1]),
                round(3760*self.multiplier[0]), round(2100*self.multiplier[1])]

    def _find_contours(self, mask:np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(contours, key=lambda x: cv2.minEnclosingCircle(x)[1], reverse=True)
        
        thresholded_contours = []
        for contour in sorted_contours:
            thresholded_contours.append(contour)
        return thresholded_contours

    def get_minimap_image(self, frame: np.ndarray) -> np.ndarray:
        x0, y0, x1, y1 = self.get_minimap_bounderies(frame)
        print(x0, y0, x1, y1)
        print(self.multiplier)
        return frame[y0:y1, x0:x1]

if __name__ == '__main__':
    map_detector = MapDetector([3840, 2160])
    image = cv2.imread(r"C:\Users\patri\Pictures\Screenshots\2025-01\TslGame_UjKKW8qwOo.jpg")
    cv2.imshow('A', cv2.resize(image, (1000, 1000)))
    cv2.waitKey(0)
    print(map_detector.is_minimap(image))