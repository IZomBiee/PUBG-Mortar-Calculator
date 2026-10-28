from pathlib import Path

import cv2
import pytest

from pubg_mortar_calculator.core.settings_loader import SettingsLoader as SL
from pubg_mortar_calculator.detectors.minimap_detector import (
    MinimapDetector,
    MinimapType,
)
from tools.yolo_mark_model.make_syn_dataset import get_annotations_from_file

FIXTURE_DIR = Path(r"tests/fixtures")


@pytest.fixture(scope="session")
def minimap_detector():
    return MinimapDetector()


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
def test_minimap_detector(minimap_detector, annotations, image_path):
    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load image at: {image_path}"

    map_size = None
    for annotation in annotations:
        annotation.x -= annotation.w / 2
        annotation.y -= annotation.h / 2
        if annotation.id == 0:
            map_size = (annotation.w, annotation.h)

    if map_size is None:
        map_size = (1, 1)

    settings = SL()

    detected_minimap_type = minimap_detector.detect(image)

    area = map_size[0] * map_size[1]

    if area > 0.5:
        actual_minimap_type = MinimapType.NO_MINIMAP
    elif area > 0.06:
        actual_minimap_type = MinimapType.LARGE_MINIMAP
    else:
        actual_minimap_type = MinimapType.SMALL_MINIMAP

    assert detected_minimap_type == actual_minimap_type, (
        f"Image: {image_path} | "
        f"Predicted: {detected_minimap_type} | Ground Truth: {actual_minimap_type}"
    )
