from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Sequence

import cv2
import numpy as np
import onnxruntime


@dataclass
class Detection:
    box: List[int]
    normalized_box: List[float]
    confidence: float
    class_name: Optional[str]
    class_nr: int

    def normalized_center_position(self) -> Tuple[float, float]:
        x0, y0, x1, y1 = self.normalized_box
        return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)

    def center_position(self) -> Tuple[int, int]:
        x0, y0, x1, y1 = self.box
        return (int((x0 + x1) / 2), int((y0 + y1) / 2))


class YoloOnnxEngine:
    def __init__(
        self,
        model_path: Path,
        classes: Optional[List[str]] = None,
        confidence: float = 0.25,
        iou_threshold: float = 0.45,
        providers: Optional[List[str]] = None,
    ) -> None:
        if providers is None:
            available = onnxruntime.get_available_providers()
            preferred = [
                "CUDAExecutionProvider",
                "TensorrtExecutionProvider",
                "CoreMLExecutionProvider",
                "DirectMLExecutionProvider",
                "CPUExecutionProvider",
            ]
            providers = [p for p in preferred if p in available]

        session_options = onnxruntime.SessionOptions()
        session_options.graph_optimization_level = (
            onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        self.session = onnxruntime.InferenceSession(
            str(model_path), sess_options=session_options, providers=providers
        )
        self.confidence = confidence
        self.iou_threshold = iou_threshold
        self.classes = classes or []

        input_tensor = self.session.get_inputs()[0]
        self.input_name = input_tensor.name
        self.input_shape = input_tensor.shape
        self.width: int = self.input_shape[-1]
        self.height: int = self.input_shape[-2]

        safe_conf = np.clip(self.confidence, 1e-6, 1.0 - 1e-6)
        self.confidence_logit: float = float(np.log(safe_conf / (1.0 - safe_conf)))

        self.last_detections: List[Detection] = []

    @staticmethod
    def letterbox_resize(
        image: np.ndarray,
        size: Tuple[int, int],
        fill_value: int = 114,
    ) -> Tuple[np.ndarray, Tuple[int, int], Tuple[float, float]]:
        target_w, target_h = size
        h, w = image.shape[:2]

        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(round(w * scale)), int(round(h * scale))

        resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        padded_img = np.full((target_h, target_w, 3), fill_value, dtype=np.uint8)
        top = (target_h - new_h) // 2
        left = (target_w - new_w) // 2
        padded_img[top : top + new_h, left : left + new_w] = resized_img

        return padded_img, (left, top), (scale, scale)

    def __preprocess_batch(
        self,
        images: Sequence[np.ndarray],
        use_letterbox: bool,
    ) -> Tuple[np.ndarray, List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[float, float]]]:
        batch_size = len(images)
        tensor = np.empty((batch_size, 3, self.height, self.width), dtype=np.float32)

        orig_sizes = []
        offsets = []
        multipliers = []

        for idx, img in enumerate(images):
            h, w = img.shape[:2]
            orig_sizes.append((w, h))

            if use_letterbox:
                padded, offset, scale = self.letterbox_resize(
                    img, (self.width, self.height)
                )
            else:
                padded = cv2.resize(
                    img, (self.width, self.height), interpolation=cv2.INTER_AREA
                )
                offset = (0, 0)
                scale = (self.width / w, self.height / h)

            offsets.append(offset)
            multipliers.append(scale)

            rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
            rgb_transposed = np.ascontiguousarray(rgb.transpose(2, 0, 1))
            tensor[idx] = rgb_transposed * (1.0 / 255.0)

        return tensor, orig_sizes, offsets, multipliers

    def __post_process_single(
        self,
        output: np.ndarray,
        orig_size: Tuple[int, int],
        offset: Tuple[int, int],
        multiplier: Tuple[float, float],
    ) -> List[Detection]:
        if output.shape[0] < output.shape[1]:
            output = output.T

        if output.shape[1] == 6 and np.max(output[:, 4]) <= 1.0:
            confidences = output[:, 4]
            mask = confidences > self.confidence
            if not np.any(mask):
                return []

            boxes = output[mask, :4]
            confidences = confidences[mask]
            class_ids = output[mask, 5].astype(int)

            xywh = np.empty_like(boxes)
            xywh[:, 0] = boxes[:, 0]
            xywh[:, 1] = boxes[:, 1]
            xywh[:, 2] = boxes[:, 2] - boxes[:, 0]
            xywh[:, 3] = boxes[:, 3] - boxes[:, 1]

        else:
            class_scores = output[:, 4:]
            raw_max_score = np.max(class_scores)
            is_logits = raw_max_score > 1.0 or np.min(class_scores) < 0.0

            if is_logits:
                max_logits = np.max(class_scores, axis=1)
                mask = max_logits > self.confidence_logit
                if not np.any(mask):
                    return []
                boxes_cxcywh = output[mask, :4]
                filtered_scores = class_scores[mask]
                confidences = 1.0 / (1.0 + np.exp(-np.max(filtered_scores, axis=1)))
                class_ids = np.argmax(filtered_scores, axis=1)
            else:
                max_scores = np.max(class_scores, axis=1)
                mask = max_scores > self.confidence
                if not np.any(mask):
                    return []
                boxes_cxcywh = output[mask, :4]
                confidences = max_scores[mask]
                class_ids = np.argmax(class_scores[mask], axis=1)

            xywh = np.empty_like(boxes_cxcywh)
            xywh[:, 0] = boxes_cxcywh[:, 0] - (boxes_cxcywh[:, 2] * 0.5)
            xywh[:, 1] = boxes_cxcywh[:, 1] - (boxes_cxcywh[:, 3] * 0.5)
            xywh[:, 2] = boxes_cxcywh[:, 2]
            xywh[:, 3] = boxes_cxcywh[:, 3]

        boxes_int = xywh.astype(int).tolist()
        confidences_list = confidences.astype(float).tolist()

        indices = cv2.dnn.NMSBoxes(
            boxes_int, confidences_list, self.confidence, self.iou_threshold
        )
        if len(indices) == 0:
            return []

        left, top = offset
        scale_x, scale_y = multiplier
        orig_w, orig_h = orig_size
        detections: List[Detection] = []

        for i in indices.flatten():
            x, y, w, h = xywh[i]
            x0 = (x - left) / scale_x
            y0 = (y - top) / scale_y
            x1 = (x + w - left) / scale_x
            y1 = (y + h - top) / scale_y

            norm_x0 = max(0.0, min(1.0, x0 / orig_w))
            norm_y0 = max(0.0, min(1.0, y0 / orig_h))
            norm_x1 = max(0.0, min(1.0, x1 / orig_w))
            norm_y1 = max(0.0, min(1.0, y1 / orig_h))

            cls_idx = int(class_ids[i])
            class_name = (
                self.classes[cls_idx] if 0 <= cls_idx < len(self.classes) else None
            )

            detections.append(
                Detection(
                    box=[
                        int(norm_x0 * orig_w),
                        int(norm_y0 * orig_h),
                        int(norm_x1 * orig_w),
                        int(norm_y1 * orig_h),
                    ],
                    normalized_box=[norm_x0, norm_y0, norm_x1, norm_y1],
                    confidence=float(confidences[i]),
                    class_name=class_name,
                    class_nr=cls_idx,
                )
            )

        return detections

    def detect_batch(
        self,
        images: Sequence[np.ndarray],
        use_letterbox_resize: bool = True,
    ) -> List[List[Detection]]:
        if not images:
            return []

        batch_tensor, orig_sizes, offsets, multipliers = self.__preprocess_batch(
            images, use_letterbox=use_letterbox_resize
        )

        raw_outputs = self.session.run(None, {self.input_name: batch_tensor})[0]

        all_detections: List[List[Detection]] = []
        for i in range(len(images)):
            detections = self.__post_process_single(
                raw_outputs[i], orig_sizes[i], offsets[i], multipliers[i]
            )
            all_detections.append(detections)

        return all_detections

    def detect(
        self, bgr_image: np.ndarray, use_letterbox_resize: bool = True
    ) -> List[Detection]:
        results = self.detect_batch([bgr_image], use_letterbox_resize)
        self.last_detections = results[0] if results else []
        return self.last_detections