import numpy as np

from ..utils import paths
from .yolov8_onnx_detector import YOLOv8OnnxDetector

class MapDetector():
    def __init__(self) -> None:
        self.detector = YOLOv8OnnxDetector(
            paths.map_detection_model(), 640,
            [
                "map"
            ],  0.85, 0.85)
    
    def detect(self, image:np.ndarray) -> tuple[int, int, int, int] | None:
        detection = self.detector.detect(image)
        if len(detection) > 0:
            detection = max(detection, key=lambda i:i['conf'])
            return detection['box']
        return None

