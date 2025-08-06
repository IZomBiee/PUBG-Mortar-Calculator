import numpy as np
from .yolov8_onnx_detector import YOLOv8OnnxDetector

class MapDetector():
    def __init__(self) -> None:
        self.detector = YOLOv8OnnxDetector('assets/map_model.onnx', 640,
            [
                "map"
            ],  0.5, 0.5)
        self.last_detection = []
    
    def detect(self, image:np.ndarray) -> list[dict]:
        self.last_detection = self.detector.detect(image)
        return self.last_detection
    
    def draw(self, image:np.ndarray) -> np.ndarray:
        return self.detector.draw(image, self.last_detection)
    
    def cut_to_map(self, image:np.ndarray) -> np.ndarray:
        if len(self.last_detection):
            detection = max(self.last_detection, key=lambda i:i['conf'])
            x0, y0, x1, y1 = detection['box']
            image = image[y0:y1, x0:x1]
        return image

