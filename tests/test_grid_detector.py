import re
from pathlib import Path

import cv2
import numpy as np
import pytest

from pubg_mortar_calculator.core.settings_loader import SettingsLoader as SL
from pubg_mortar_calculator.detectors import GridDetector
from tools.yolo_mark_model.make_syn_dataset import get_annotations_from_file

FIXTURE_DIR = Path(r"tests/fixtures")
MAX_ERROR = 0.05


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


@pytest.mark.parametrize("annotations, image_path", load_test_images())
def test_grid_gap(annotations, image_path):
    grid_detector = GridDetector()

    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load image at: {image_path}"
    h, w = image.shape[:2]

    grid_gap = None
    map_box = None
    for annotation in annotations:
        annotation.x -= annotation.w / 2
        annotation.y -= annotation.h / 2
        if annotation.id == 0:
            x0 = int(annotation.x * w)
            y0 = int(annotation.y * h)
            map_box = (x0, y0, x0 + int(annotation.w * w), y0 + int(annotation.h * h))
        elif annotation.id == 13:
            grid_gap = (annotation.w * w + annotation.h * h) / 2

    assert grid_gap is not None, f"Failed to load grid gap at: {image_path}"

    if map_box is not None:
        x0, y0, x1, y1 = map_box
        image = image[y0:y1, x0:x1]

    settings = SL()

    canny = grid_detector.get_canny_image(
        image,
        settings.get("grid_detection_canny1_threshold_slider"),
        settings.get("grid_detection_canny2_threshold_slider"),
    )

    lines = grid_detector.get_normalized_lines(
        canny,
        settings.get("grid_detection_line_threshold_slider") / 100,
        settings.get("grid_detection_line_gap_slider") / 100,
        settings.get("grid_detection_merge_threshold_slider"),
    )

    calc_gap = grid_detector.calculate_grid_gap(*lines)

    assert calc_gap is not None, f"Image: {image_path} | Ground Truth: {grid_gap}"

    # if calc_gap != pytest.approx(grid_gap, abs=MAX_DELTA):
    #     grid_detector.draw_lines(image, *lines)
    #     cv2.imshow("A", cv2.resize(image, (800, 800)))
    #     cv2.waitKey(0)

    max_delta = round(((image.shape[0] + image.shape[1]) / 2) * MAX_ERROR)

    assert calc_gap == pytest.approx(grid_gap, abs=max_delta), (
        f"Image: {image_path} | "
        f"Delta: {abs(calc_gap - grid_gap)} | "
        f"Predicted: {calc_gap} | Ground Truth: {grid_gap}"
    )
