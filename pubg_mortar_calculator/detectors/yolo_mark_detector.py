import random

import cv2
import numpy as np

from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.detectors.yolo_onnx_detector import (
    Detection,
    YoloOnnxDetector,
)

from ..utils import paths


class YoloMarkDetector:
    def __init__(self) -> None:
        self.detector = YoloOnnxDetector(
            paths.mark_detection_model(),
            [
                "yellow_mark",
                "yellow_player_mark",
                "orange_mark",
                "orange_player_mark",
                "blue_mark",
                "blue_player_mark",
                "green_mark",
                "green_player_mark",
            ],
            0.1,
            0.1,
        )

    def get_player_and_mark_pos(
        self, samples: list[tuple[tuple[int, int], np.ndarray]], color: str
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
        self, samples: list[tuple[tuple[int, int], np.ndarray]]
    ) -> list[Detection]:
        unique_detections = []

        for (x, y), sample in samples:
            detections = self._detect(sample)
            for detection in detections:
                detection.box[0] += x
                detection.box[1] += y
                detection.box[2] += x
                detection.box[3] += y

                if not self.__is_in_list(unique_detections, detection):
                    unique_detections.append(detection)

        return unique_detections

    def __is_in_list(
        self, unique_list: list[Detection], detection: Detection, theshold: int = 10
    ) -> bool:
        for unique_detection in unique_list:
            if unique_detection.class_nr != detection.class_nr:
                continue
            delta_x = abs(unique_detection.box[0] - detection.box[0])
            delta_y = abs(unique_detection.box[1] - detection.box[1])

            if delta_x + delta_y < theshold:
                return True
        return False

    def make_samples(
        self,
        image: np.ndarray,
        positions: list[tuple[int, int, float]],
        margin_multiplier: float = 3,
    ) -> list[tuple[tuple[int, int], np.ndarray]]:
        samples = []
        height, width = image.shape[:2]

        for x, y, r in positions:
            margin = max(round(r * margin_multiplier), 50)
            x_min = max(0, x - margin)
            x_max = min(width, x + margin)
            y_min = max(0, y - margin)
            y_max = min(height, y + margin)

            crop = image[y_min:y_max, x_min:x_max]

            samples.append(((x_min, y_min), crop))

        return samples

    def change_confidence(self, confidence: float):
        self.detector.confidence = confidence
        self.detector.iou_threshold = confidence

    def _detect(self, image: np.ndarray) -> list[Detection]:
        detections = self.detector.detect(image)
        return detections


def main():
    image = cv2.imread(
        r"tests\fixtures\desert_map_green_636_495_1226_481.jpg"
    )
    if image is None:
        exit("No image found")

    hsv_mark_detector.remove_danger_zones(image)
    mask = hsv_mark_detector.get_roi_hsv_mask(image, "green")
    contours = hsv_mark_detector._find_contours(mask)
    positions = hsv_mark_detector.get_all_positions(mask)
    yolo_detector = YoloMarkDetector()
    samples = yolo_detector.make_samples(image, positions)

    for sample in samples:
        cv2.imshow("B", cv2.resize(sample[1], (500, 500)))
        cv2.waitKey(0)

    detections = yolo_detector._get_unique_detections(samples)

    player, mark = yolo_detector.get_player_and_mark_pos(samples, "green")
    for d in detections:
        cv2.circle(image, d.center_position(), random.randint(10, 40), (0, 0, 255), 2)
    if player is not None:
        cv2.circle(image, player, 15, (255, 0, 255), 5)
    if mark is not None:
        cv2.circle(image, mark, 15, (255, 0, 255), 5)

    cv2.drawContours(image, contours, -1, (255, 0, 255), 2)
    cv2.imshow("A", cv2.resize(image, (1000, 1000)))
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
