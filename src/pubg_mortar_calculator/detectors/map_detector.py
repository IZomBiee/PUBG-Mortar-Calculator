import numpy as np
import cv2 

from ..utils import paths
from src.yolo11_onnx_detector import Yolo11OnnxDetector

class MapDetector():
    def __init__(self) -> None:
        self.detector = Yolo11OnnxDetector(
            paths.map_detection_model(), ['map'], 0.8, 0.5)
    
    def detect(self, image:np.ndarray) -> list[int] | None:
        detections = self.detector.detect(image)
        if len(detections) > 0:
            detection = max(detections, key=lambda i:i.confidence)
            return detection.box
        return None

if __name__ == '__main__':
    detector = MapDetector()
    image = cv2.imread(r'D:\Projects\Python\PUBG-Mortar-Calculator\assets\elevation_preview.png')
    box = detector.detect(image)
    if box is not None:
        x0, y0, x1, y1 = box
        cv2.rectangle(image, (x0, y0), (x1, y1), (255, 255, 255), 5)
    cv2.imshow("Test", cv2.resize(image, (800, 600)))
    cv2.waitKey(0)