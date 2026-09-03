import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pytest

from pubg_mortar_calculator.core.settings_loader import SettingsLoader as SL
from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.detectors.yolo_mark_detector import YoloMarkDetector
from tools.mark_model.make_dataset import Annotation, get_annotations_from_file

FIXTURE_DIR = Path(r"tests/fixtures")
MAX_DELTA = 10

def load_test_images():
    test_cases = []
    for image_path in FIXTURE_DIR.glob("*.jpg"):
        annotations_path = image_path.with_suffix(".txt")
        if annotations_path.exists():
            annotations = get_annotations_from_file(annotations_path)
        else:
            annotations = []

        test_cases.append((annotations, image_path))

    return test_cases


@dataclass
class Mark:
    color: str
    is_player: bool
    x: float
    y: float
    w: float
    h: float

    def to_string(self):
        if self.is_player:
            return f"{self.color}_player_mark"
        else:
            return f"{self.color}_mark"


def annotation_to_mark(annotation: Annotation) -> Mark:
    color = ""
    player = False
    match annotation.id:
        case 1:
            color = "yellow"
        case 2:
            color = "yellow"
            player = True
        case 3:
            color = "orange"
        case 4:
            color = "orange"
            player = True
        case 5:
            color = "blue"
        case 6:
            color = "blue"
            player = True
        case 7:
            color = "green"
        case 8:
            color = "green"
            player = True

    return Mark(color, player, annotation.x, annotation.y, annotation.w, annotation.h)


@pytest.mark.parametrize("annotations, image_path", load_test_images())
def test_yolo_detection(annotations, image_path):
    detector = YoloMarkDetector()

    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load image at: {image_path}"
    h, w = image.shape[:2]

    map_box = None
    marks: list[Annotation] = []
    for annotation in annotations:
        annotation.x -= annotation.w / 2
        annotation.y -= annotation.h / 2
        if annotation.id == 0:
            x0 = int(annotation.x * w)
            y0 = int(annotation.y * h)
            map_box = (x0, y0, x0 + int(annotation.w * w), y0 + int(annotation.h * h))
        elif annotation.id <= 8:
            marks.append(annotation)

    if map_box is not None:
        x0, y0, x1, y1 = map_box
        image = image[y0:y1, x0:x1]
    else:
        hsv_mark_detector.remove_danger_zones(image)

    for true_annotation in marks:
        true_mark = annotation_to_mark(true_annotation)
        assert true_mark.color != "", f"Image: {image_path} | No true color loaded"

        mask = hsv_mark_detector.get_roi_hsv_mask(image, true_mark.color)
        roi = hsv_mark_detector.get_all_positions(mask)

        samples = detector.make_samples(image, roi)
        # for sample in samples:
        #     cv2.imshow("A", cv2.resize(sample[1], (800, 800)))
        #     cv2.waitKey(0)

        detections = detector._get_unique_detections(samples)

        cls_names = [i.class_name for i in detections]
        assert true_mark.to_string() in cls_names, (
            f"Image: {image_path} | Not found {true_mark}"
        )


if __name__ == "__main__":
    for sample in load_test_images():
        test_yolo_detection(*sample)
