from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

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
        return (int((x0 + x1) / 2), int((y0 + y1) / 2))

    def center_position(self) -> Tuple[int, int]:
        x0, y0, x1, y1 = self.box
        return (int((x0 + x1) / 2), int((y0 + y1) / 2))


class YoloOnnxDetector:
    def __init__(
        self,
        model_path: Path,
        classes: List[str] = [],
        confidence: float = 0.25,
        iou_threshold: float = 0.45,
    ) -> None:
        self.session = onnxruntime.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.confidence = confidence
        self.iou_threshold = iou_threshold
        self.classes = classes

        input_tensor = self.session.get_inputs()[0]
        self.input_shape = input_tensor.shape
        self.width, self.height = self.input_shape[-1], self.input_shape[-2]

        self.last_letterbox_offset = (0, 0)
        self.last_letterbox_multiplier = (1.0, 1.0)
        self.last_original_image_size = None
        self.last_detections: List[Detection] = []

    def __preprocess_image(self, image: np.ndarray) -> np.ndarray:
        image = image.astype(np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, axis=0)
        return image

    def __inference(self, processed_image: np.ndarray) -> np.ndarray:
        input_name = self.session.get_inputs()[0].name
        return self.session.run(None, {input_name: processed_image})[0]

    def __post_process_outputs(self, raw_outputs: np.ndarray) -> List[Detection]:
        outputs = np.squeeze(raw_outputs)

        if outputs.ndim != 2:
            return []

        if outputs.shape[0] < outputs.shape[1]:
            outputs = outputs.T

        if outputs.shape[1] == 6 and np.max(outputs[:, 4]) <= 1.0:
            boxes_x1y1x2y2 = outputs[:, :4]
            confidences = outputs[:, 4]
            class_ids = outputs[:, 5].astype(int)

            mask = confidences > self.confidence
            boxes_x1y1x2y2 = boxes_x1y1x2y2[mask]
            confidences = confidences[mask]
            class_ids = class_ids[mask]

            if len(confidences) == 0:
                return []

            xywh = np.zeros_like(boxes_x1y1x2y2)
            xywh[:, 0] = boxes_x1y1x2y2[:, 0]
            xywh[:, 1] = boxes_x1y1x2y2[:, 1]
            xywh[:, 2] = boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0]
            xywh[:, 3] = boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1]

        else:
            boxes_cxcywh = outputs[:, :4]
            class_scores = outputs[:, 4:]

            # Convert unnormalized logits to probabilities if needed
            if np.max(class_scores) > 1.0 or np.min(class_scores) < 0.0:
                class_scores = 1.0 / (1.0 + np.exp(-class_scores))

            class_ids = np.argmax(class_scores, axis=1)
            confidences = np.max(class_scores, axis=1)

            mask = confidences > self.confidence
            boxes_cxcywh = boxes_cxcywh[mask]
            confidences = confidences[mask]
            class_ids = class_ids[mask]

            if len(confidences) == 0:
                return []

            xywh = np.zeros_like(boxes_cxcywh)
            xywh[:, 0] = boxes_cxcywh[:, 0] - (boxes_cxcywh[:, 2] / 2)
            xywh[:, 1] = boxes_cxcywh[:, 1] - (boxes_cxcywh[:, 3] / 2)
            xywh[:, 2] = boxes_cxcywh[:, 2]
            xywh[:, 3] = boxes_cxcywh[:, 3]

        boxes_int = xywh.astype(int).tolist()
        confidences_list = confidences.astype(float).tolist()

        indices = cv2.dnn.NMSBoxes(
            boxes_int, confidences_list, self.confidence, self.iou_threshold
        )

        detections = []
        if len(indices) > 0:
            indices = indices.flatten()
            left, top = self.last_letterbox_offset
            scale_x, scale_y = self.last_letterbox_multiplier

            for i in indices:
                x, y, w, h = xywh[i]

                if self.last_original_image_size is not None:
                    orig_w, orig_h = self.last_original_image_size
                    x0 = (x - left) / scale_x
                    y0 = (y - top) / scale_y
                    x1 = (x + w - left) / scale_x
                    y1 = (y + h - top) / scale_y

                    norm_x0 = max(0.0, min(1.0, x0 / orig_w))
                    norm_y0 = max(0.0, min(1.0, y0 / orig_h))
                    norm_x1 = max(0.0, min(1.0, x1 / orig_w))
                    norm_y1 = max(0.0, min(1.0, y1 / orig_h))

                    normalized_box = [norm_x0, norm_y0, norm_x1, norm_y1]
                    pixel_box = [
                        int(norm_x0 * orig_w),
                        int(norm_y0 * orig_h),
                        int(norm_x1 * orig_w),
                        int(norm_y1 * orig_h),
                    ]
                else:
                    norm_x0 = max(0.0, min(1.0, x / self.width))
                    norm_y0 = max(0.0, min(1.0, y / self.height))
                    norm_x1 = max(0.0, min(1.0, (x + w) / self.width))
                    norm_y1 = max(0.0, min(1.0, (y + h) / self.height))

                    normalized_box = [norm_x0, norm_y0, norm_x1, norm_y1]
                    pixel_box = [
                        int(norm_x0 * self.width),
                        int(norm_y0 * self.height),
                        int(norm_x1 * self.width),
                        int(norm_y1 * self.height),
                    ]

                cls_idx = int(class_ids[i])
                class_name = (
                    self.classes[cls_idx] if 0 <= cls_idx < len(self.classes) else None
                )

                detections.append(
                    Detection(
                        box=pixel_box,
                        normalized_box=normalized_box,
                        confidence=float(confidences[i]),
                        class_name=class_name,
                        class_nr=cls_idx,
                    )
                )

        return detections

    def _get_color(self, class_id: int) -> Tuple[int, int, int]:
        np.random.seed(class_id * 999)
        return tuple(int(c) for c in np.random.randint(60, 255, size=3))

    def detect(
        self, bgr_image: np.ndarray, use_letterbox_resize: bool = True
    ) -> List[Detection]:
        if use_letterbox_resize:
            self.last_original_image_size = (bgr_image.shape[1], bgr_image.shape[0])
            bgr_image, self.last_letterbox_offset, self.last_letterbox_multiplier = (
                self.letterbox_resize(bgr_image, (self.width, self.height))
            )
        else:
            self.last_letterbox_offset, self.last_letterbox_multiplier = (
                (
                    0,
                    0,
                ),
                (1.0, 1.0),
            )
            self.last_original_image_size = None

        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        processed_image = self.__preprocess_image(rgb_image)
        raw_outputs = self.__inference(processed_image)
        self.last_detections = self.__post_process_outputs(raw_outputs)

        return self.last_detections

    def draw_last_detections(self, image: np.ndarray) -> None:
        h, w = image.shape[:2]
        font_scale = max(0.4, min(w, h) / 1200.0)
        thickness = max(1, int(font_scale * 2))

        for det in self.last_detections:
            x0, y0, x1, y1 = det.normalized_box
            x0, y0 = int(x0 * w), int(y0 * h)
            x1, y1 = int(x1 * w), int(y1 * h)

            color = self._get_color(det.class_nr)
            cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)

            class_label = det.class_name if det.class_name else f"Class {det.class_nr}"
            label = f"{class_label} {det.confidence:.2f}"

            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )

            text_y0 = max(y0, text_h + 4)
            cv2.rectangle(
                image,
                (x0, text_y0 - text_h - 4),
                (x0 + text_w + 4, text_y0 + baseline),
                color,
                -1,
            )
            cv2.putText(
                image,
                label,
                (x0 + 2, text_y0 - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA,
            )

    @staticmethod
    def letterbox_resize(
        image: np.ndarray, size: Tuple[int, int], fill_value: int = 114
    ) -> Tuple[np.ndarray, Tuple[int, int], Tuple[float, float]]:
        target_w, target_h = size
        h, w = image.shape[:2]

        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(round(w * scale)), int(round(h * scale))

        resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        padded_img = np.full((target_h, target_w, 3), fill_value, dtype=image.dtype)
        top = (target_h - new_h) // 2
        left = (target_w - new_w) // 2
        padded_img[top : top + new_h, left : left + new_w] = resized_img

        return padded_img, (left, top), (scale, scale)


import argparse


def main():
    parser = argparse.ArgumentParser(description="Run YOLO ONNX detection")
    parser.add_argument("-m", "--model", type=str, required=True)
    parser.add_argument("-i", "--image", type=str, required=True)
    parser.add_argument("-c", "--conf", type=float, default=0.25)
    args = parser.parse_args()

    detector = YoloOnnxDetector(Path(args.model), confidence=args.conf)
    image = cv2.imread(args.image)

    if image is None:
        print(f"Error: Could not load image {args.image}")
        return

    detections = detector.detect(image)
    print(f"Found {len(detections)} detections.")

    detector.draw_last_detections(image)
    cv2.imshow("Detection", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
