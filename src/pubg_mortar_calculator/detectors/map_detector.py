import numpy as np

from src.yolo11_onnx_detector import Yolo11OnnxDetector

from ..utils import paths


class MapDetector:
    def __init__(self) -> None:
        self.detector = Yolo11OnnxDetector(
            paths.map_detection_model(), ["map"], 0.2, 0.2
        )

    def detect(self, image: np.ndarray) -> list[int] | None:
        detections = self.detector.detect(image)
        if len(detections) > 0:
            detection = max(detections, key=lambda i: i.confidence)
            return detection.box
        return None
