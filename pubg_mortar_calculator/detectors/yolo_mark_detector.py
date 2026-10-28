import cv2
import numpy as np

from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.detectors.yolo_onnx_engine import (
    Detection,
    YoloOnnxEngine,
)
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
from ..utils import paths
from dataclasses import dataclass

class YoloMarkDetector:
    def __init__(self) -> None:
        self.base_height = 1080.0
        self.base_aspect = 16.0 / 9.0

        self.classes = [
            'yellow_mark', 'yellow_player_mark', 'orange_mark',
            'orange_player_mark', 'blue_mark', 'blue_player_mark',
            'green_mark', 'green_player_mark'
        ]

        self.detector = YoloOnnxEngine(
            paths.mark_detection_model(),
            self.classes,
            0.1,
            0.3,
        )

    def get_player_and_mark_pos(
        self, samples: list[tuple[tuple[int, int, int, int], np.ndarray]], color: str
    ) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
        detections = self._get_unique_detections(samples)

        player_pos, mark_pos = None, None
        for detection in detections:
            if detection.class_name is not None and color in detection.class_name:
                if "player" in detection.class_name and player_pos is None:
                    player_pos = detection.center_position()
                elif mark_pos is None:
                    mark_pos = (detection.center_position()[0], detection.box[3])

        return (player_pos, mark_pos)

    def _get_unique_detections(
        self, samples: list[tuple[tuple[int, int, int, int], np.ndarray]]
    ) -> list[Detection]:
        unique_detections: list[Detection] = []

        for (x, y, w, h), sample in samples:
            scale_x = w/sample.shape[1]
            scale_y = h/sample.shape[0]

            detections = self._detect(sample)
            for detection in detections:
                detection.box[0] = round(x + detection.box[0] * scale_x)
                detection.box[1] = round(y + detection.box[1] * scale_y)
                detection.box[2] = round(x + detection.box[2] * scale_x)
                detection.box[3] = round(y + detection.box[3] * scale_y)

                while True:
                    unique_detection = self._find_detection_in_list(unique_detections, detection)
                    if unique_detection is None:
                        unique_detections.append(detection)
                        break
                    else:
                        if unique_detection.confidence > detection.confidence or unique_detection is detection:
                            break
                        else:
                            unique_detections[unique_detections.index(unique_detection)] = detection

        unique_detections.sort(key=lambda det: det.confidence, reverse=True)

        return unique_detections

    # def __process_extra_marks(self, detections: list[Detection]) -> list[Detection]:
    #     for category in self.classes:
    #         category_detections = list(filter(lambda detection: detection.class_name == category,
    #             detections))
    #         category_detections.sort(key=lambda detection: detection.confidence)
    #         if len(category_detections) > 1:
    #             len


    @staticmethod
    def _find_detection_in_list(
        unique_list: list[Detection], detection: Detection, theshold: int = 15
    ) -> Detection | None:
        for unique_detection in unique_list:
            delta_x = abs(unique_detection.box[0] - detection.box[0])
            delta_y = abs(unique_detection.box[1] - detection.box[1])

            if delta_x + delta_y < theshold:
                return unique_detection
        return None

    def make_samples(
        self,
        image: np.ndarray,
        positions: list[tuple[int, int, float]],
        actual_resolution: tuple[int, int] | None = None,
    ) -> list[tuple[tuple[int, int, int, int], np.ndarray]]:
        img_h, img_w = image.shape[:2]

        if actual_resolution is None:
            h, w = img_h, img_w
        else:
            w, h = actual_resolution

        scale_y = h / self.base_height
        aspect = w / h
        base_aspect = self.base_aspect
        aspect_factor = aspect / base_aspect
        crop_h = int(round(self.detector.height * scale_y))

        if aspect < base_aspect:
            crop_w = int(round(self.detector.width * scale_y * aspect_factor))
        else:
            crop_w = crop_h

        crop_w = min(img_w, crop_w)
        crop_h = min(img_h, crop_h)

        half_w = crop_w // 2
        half_h = crop_h // 2

        samples = []
        for x, y, r in positions:
            x_min = max(0, min(x - half_w, img_w - crop_w))
            y_min = max(0, min(y - half_h, img_h - crop_h))

            crop = image[y_min : y_min + crop_h, x_min : x_min + crop_w]

            samples.append(((x_min, y_min, crop_w, crop_h), crop))

        return samples

    def change_confidence(self, confidence: float):
        self.detector.confidence = confidence
        self.detector.iou_threshold = confidence

    def _detect(self, image: np.ndarray) -> list[Detection]:
        detections = self.detector.detect(image)
        return detections


def main():
    image_bgr = cv2.imread(r"temp\map_preview.png")
    if image_bgr is None:
        raise FileNotFoundError("No image found!")

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mask = hsv_mark_detector.get_roi_hsv_mask(image_bgr, "green")
    positions = hsv_mark_detector.get_all_positions(mask)
    yolo_detector = YoloMarkDetector()
    samples = yolo_detector.make_samples(image_bgr, positions)
    detections = yolo_detector._get_unique_detections(samples)

    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.imshow(image_rgb)
    ax.axis("off")

    color_palette = {
        "player": "#00E5FF",
        "mark": "#FF1744",
        "default": "#00FFAA",
    }

    for det in detections:
        x1, y1, x2, y2 = det.box[:4]
        w, h = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        label_name = str(det.class_name).lower()
        if "player" in label_name:
            theme_color = color_palette["player"]
        elif "mark" in label_name:
            theme_color = color_palette["mark"]
        else:
            theme_color = color_palette["default"]

        box = patches.FancyBboxPatch(
            (x1, y1),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=4",
            linewidth=2,
            edgecolor=theme_color,
            facecolor="none",
        )
        ax.add_patch(box)

        ax.text(
            x1,
            y1 - 6,
            f'{det.class_name} - {round(det.confidence, 2)}',
            fontsize=9,
            fontweight="bold",
            color="white",
            verticalalignment="bottom",
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor=theme_color,
                edgecolor="none",
                alpha=0.85,
            ),
            path_effects=[withStroke(linewidth=1.5, foreground="black")],
        )

    plt.tight_layout(pad=0)
    plt.show()


if __name__ == "__main__":
    main()
