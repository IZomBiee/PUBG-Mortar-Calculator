import onnxruntime
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Detection:
    box: List[int]
    normalized_box: List[float]
    confidence: float
    class_name: Optional[str]
    class_nr: int

class Yolo11OnnxDetector:
    def __init__(self, model_path: str, classes: List[str] = [],
                 confidence: float = 0.05,
                 iou_threshold: float = 0.05) -> None:
        self.session = onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.confidence = confidence

        self.input_shape = self.session.get_inputs()[0].shape
        self.width, self.height = self.input_shape[-1], self.input_shape[-2]
        self.input_dtype = np.float16 if self.session.get_inputs()[0].type == "tensor(float16)" else np.float32

        self.last_letterbox_offset = (0, 0)
        self.last_letterbox_multiplier = (1.0, 1.0)
        self.last_original_image_size = None
        self.last_detections: List[Detection] = []
        self.classes = classes
        self.iou_threshold = iou_threshold

    def __preprocess_image(self, image: np.ndarray) -> np.ndarray:
        image = image.astype(self.input_dtype) / 255.0
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, axis=0)
        return image

    def __inference(self, processed_image: np.ndarray) -> np.ndarray:
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: processed_image})[0][0] # type: ignore
        outputs = np.transpose(outputs, (1, 0))
        return outputs

    def __post_process_outputs(self, raw_outputs: np.ndarray) -> List[Detection]:
        boxes, confidences, class_ids = [], [], []

        for output in raw_outputs:
            x_center, y_center, w, h = map(float, output[:4])
            half_w, half_h = w / 2, h / 2
            x0, y0, x1, y1 = x_center - half_w, y_center - half_h, x_center + half_w, y_center + half_h

            confidences_arr = output[4:]
            confidence = float(np.max(confidences_arr))
            class_nr = int(np.argmax(confidences_arr))

            if confidence > self.confidence:
                boxes.append([int(x0),
                              int(y0),
                              int(x1 - x0),
                              int(y1 - y0)])  # x, y, w, h for NMS
                confidences.append(confidence)
                class_ids.append(class_nr)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.iou_threshold)

        detections = []
        if len(indices) > 0:
            for i in indices.flatten():  # type: ignore
                if self.last_original_image_size is not None:
                    boxes[i][0] -= self.last_letterbox_offset[0]
                    boxes[i][1] -= self.last_letterbox_offset[1]
                    boxes[i][0] /= self.last_letterbox_multiplier[0]
                    boxes[i][1] /= self.last_letterbox_multiplier[1]
                    boxes[i][2] /= self.last_letterbox_multiplier[0]
                    boxes[i][3] /= self.last_letterbox_multiplier[1]
                    normalized_box = [boxes[i][0]/self.last_original_image_size[0],
                                      boxes[i][1]/self.last_original_image_size[1],
                                      (boxes[i][2]/self.last_original_image_size[0])+(boxes[i][0]/self.last_original_image_size[0]),
                                      (boxes[i][3]/self.last_original_image_size[1])+(boxes[i][1]/self.last_original_image_size[1])]
                else:
                    normalized_box = [boxes[i][0]/self.width,
                    boxes[i][1]/self.height,
                    boxes[i][2]/self.width,
                    boxes[i][3]/self.height] 

                class_name = self.classes[class_ids[i]] if 0 <= class_ids[i] < len(self.classes) else None
                detections.append(Detection(
                    box=[int(boxes[i][0]),
                         int(boxes[i][1]),
                         int(boxes[i][0]+boxes[i][2]),
                         int(boxes[i][1]+boxes[i][3])],
                    normalized_box=normalized_box,
                    confidence=confidences[i],
                    class_name=class_name,
                    class_nr=class_ids[i]
                ))
        return detections

    def _get_color(self, class_id: int) -> tuple[int, int, int]:
        np.random.seed(class_id * 999)
        return tuple(int(x) for x in np.random.randint(60, 255, size=3)) # type: ignore

    def detect(self, image: np.ndarray, use_lettebox_resize:bool = True) -> List[Detection]:
        if use_lettebox_resize:
            self.last_original_image_size = (image.shape[1], image.shape[0])
            (image, self.last_letterbox_offset, self.last_letterbox_multiplier) =\
            self.letterbox_resize(image, (self.width, self.height))
        else:
            self.last_letterbox_offset, self.last_letterbox_offset = (0, 0), (1.0, 1.0)
            self.last_original_image_size = None
        processed_image = self.__preprocess_image(image)
        raw_outputs = self.__inference(processed_image)
        self.last_detections = self.__post_process_outputs(raw_outputs)
        return self.last_detections

    def draw_last_detections(self, image: np.ndarray) -> None:
        h, w = image.shape[:2]
        for idx, det in enumerate(self.last_detections):
            x0, y0, x1, y1 = det.normalized_box
            print(x0, y0, x1, y1)

            x0, y0 = int(x0*w), int(y0*h)
            x1, y1 = int(x1*w), int(y1*h)
            color = self._get_color(det.class_nr)
            cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)

            class_label = det.class_name if det.class_name else f"Class {det.class_nr}"
            label = f"{class_label} {det.confidence:.2f}"

            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 2, 5)
            cv2.rectangle(image, (x0, y0 - text_h - 6), (x0 + text_w + 2, y0), color, -1)
            cv2.putText(image, label, (x0 + 2, y0 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)

    @staticmethod
    def letterbox_resize(image: np.ndarray, size: Tuple[int, int], fill_value: int = 114) -> Tuple[np.ndarray, Tuple[int, int], Tuple[float, float]]:
        target_h, target_w = size
        h, w = image.shape[:2]

        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        padded_img = np.full((target_h, target_w, 3), fill_value, dtype=image.dtype)
        top = (target_h - new_h) // 2
        left = (target_w - new_w) // 2
        padded_img[top:top + new_h, left:left + new_w] = resized_img

        offset = (left, top)
        multiplier = (scale, scale)
        return padded_img, offset, multiplier
