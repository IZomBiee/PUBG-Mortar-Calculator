import cv2
import numpy as np

class MapDetector:
    def __init__(self):
        ...
    
    def _process_frame(self, frame:np.ndarray) -> np.ndarray:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # canny_frame = cv2.Canny(gray_frame, 150,
        #                         50, apertureSize=3)
        thresholded_frame = cv2.threshold(gray_frame, 230, 255, cv2.THRESH_BINARY)[1]
        blur_frame = cv2.GaussianBlur(thresholded_frame, (71, 71), 15)
        thresholded_frame = cv2.threshold(blur_frame, 15, 255, cv2.THRESH_BINARY)[1]

        return thresholded_frame

    def _find_contours(self, mask:np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        thresholded_contours = []
        for contour in sorted_contours:
            thresholded_contours.append(contour)
        return thresholded_contours

    def detect_map_size(self, frame:np.ndarray) -> str:
        minimap_frame = frame[1100:2160, 2500:3840]
        processed_frame = self._process_frame(minimap_frame)

        contours = self._find_contours(processed_frame)
        for contour in contours:
            x0, y0, x1, y1 = cv2.boundingRect(contour)
            cv2.rectangle(minimap_frame, (x0, y0), (x1, y1), (120), 1)

    
    def get_map_bounderies(self) -> list[int, int, int, int]:
        ...

if __name__ == '__main__':
    map_detector = MapDetector()
    frame = cv2.imread(r"C:\Users\patri\Pictures\Screenshots\2025-03\TslGame_18rUr6MrLH.jpg")
    print(map_detector.detect_map_size(frame))
    cv2.imshow("Game", cv2.resize(frame, (1000, 1000)))
    cv2.waitKey(0)
