import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path

class ONNXClassificator:
    def __init__(self, path: Path) -> None:
        self.session = ort.InferenceSession(
            path, providers=["CPUExecutionProvider"]
        )
        input_tensor = self.session.get_inputs()[0]
        self.input_shape = input_tensor.shape
        self.width, self.height = self.input_shape[-1], self.input_shape[-2]

    def detect(self, bgr_image: np.ndarray) -> int:
        pred_class_id = int(np.argmax(self._get_probs(bgr_image)))
        return pred_class_id

    def _get_probs(self, bgr_image: np.ndarray) -> np.ndarray:
        bgr_image = self._full_preprocess(bgr_image)
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name

        outputs = self.session.run([output_name], {input_name: [bgr_image]})
        logits = outputs[0][0]  # type: ignore

        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)

    def _full_preprocess(self, image: np.ndarray):
        return self._transpose(self._normalize(self._basic_preprocess(image)))

    def _basic_preprocess(self, bgr_image: np.ndarray) -> np.ndarray:
        image = self._letterbox(bgr_image)
        image = cv2.resize(image, (self.width, self.height), interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    @staticmethod 
    def _normalize(rgb_image: np.ndarray) -> np.ndarray:
        image = rgb_image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        return (image - mean) / std

    @staticmethod
    def _transpose(float_image: np.ndarray) -> np.ndarray:
        return float_image.transpose((2, 0, 1))

    @staticmethod
    def _letterbox(image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        max_dim = max(w, h)

        pad_left = (max_dim - w) // 2
        pad_top = (max_dim - h) // 2
        pad_right = max_dim - w - pad_left
        pad_bottom = max_dim - h - pad_top

        return cv2.copyMakeBorder(
            image,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )