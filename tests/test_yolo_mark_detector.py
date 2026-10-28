import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import pytest

from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.detectors.yolo_mark_detector import YoloMarkDetector
from tools.yolo_mark_model.make_syn_dataset import Annotation, get_annotations_from_file

FIXTURE_DIR = Path(r"tests/fixtures")
MAX_DELTA = 0.05


def load_test_images():
    test_cases = []

    for image_path in FIXTURE_DIR.iterdir():
        if image_path.suffix.lower() in (".webp", ".jpg", ".png"):
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

    image = cv2.imread(str(image_path))
    assert image is not None, f"Failed to load image at: {image_path}"
    h, w = image.shape[:2]

    map_box = None
    marks: list[Annotation] = []

    for annotation in annotations:
        if annotation.id == 0:
            top_left_x = annotation.x - annotation.w / 2
            top_left_y = annotation.y - annotation.h / 2
            x0 = int(top_left_x * w)
            y0 = int(top_left_y * h)
            map_box = (x0, y0, x0 + int(annotation.w * w), y0 + int(annotation.h * h))
        elif annotation.id <= 8:
            marks.append(annotation)

    offset_x = 0
    offset_y = 0
    if map_box is not None:
        x0, y0, x1, y1 = map_box
        image = image[y0:y1, x0:x1]
        offset_x = x0
        offset_y = y0

    curr_h = image.shape[0]
    max_allowed_pixel_delta = MAX_DELTA * curr_h

    for true_annotation in marks:
        true_mark = annotation_to_mark(true_annotation)
        assert true_mark.color != "", f"Image: {image_path} | No true color loaded"

        mask = hsv_mark_detector.get_roi_hsv_mask(image, true_mark.color)
        if map_box is None:
            hsv_mark_detector.remove_danger_zones(mask)
        roi = hsv_mark_detector.get_all_positions(mask)

        samples = detector.make_samples(image, roi, (w, h))
        detections = detector._get_unique_detections(samples)

        expected_class = true_mark.to_string()
        matching_detections = [d for d in detections if d.class_name == expected_class]

        assert len(matching_detections) > 0, (
            f"Image: {image_path} | Not found {expected_class} | "
            f"Detections: {[d.class_name for d in detections]}"
        )

        expected_cx = (true_annotation.x * w) - offset_x
        expected_cy = (true_annotation.y * h) - offset_y

        closest_distance = float("inf")
        closest_det = None

        for det in matching_detections:
            det_cx, det_cy = det.center_position()
            dist = math.hypot(det_cx - expected_cx, det_cy - expected_cy)
            if dist < closest_distance:
                closest_distance = dist
                closest_det = det

        assert closest_distance <= max_allowed_pixel_delta, (
            f"Image: {image_path} | Mark: {expected_class} position delta too large! "
            f"Distance: {closest_distance:.2f}px ({closest_distance / curr_h:.2%}), "
            f"Allowed: {max_allowed_pixel_delta:.2f}px ({MAX_DELTA:.2%}). "
            f"Expected: ({expected_cx:.1f}, {expected_cy:.1f}), "
            f"Got: {closest_det.center_position()} (Box: {closest_det.box})"
        )


if __name__ == "__main__":
    for sample in load_test_images():
        test_yolo_detection(*sample)