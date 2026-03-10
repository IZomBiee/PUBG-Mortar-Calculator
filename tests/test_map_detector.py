import re
from pathlib import Path

import cv2
import pytest

# TODO: Replace with your actual YOLO detector import
from src.pubg_mortar_calculator.detectors import MapDetector

# Point to your minimaps fixture directory
FIXTURE_DIR = Path("tests/fixtures/maps")


def load_minimap_images():
    """Dynamically loads test cases and 4 coordinates from filenames."""
    test_cases = []

    if not FIXTURE_DIR.exists():
        return test_cases

    for img_path in FIXTURE_DIR.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            # Match filenames like "desert_zoom_10_20_150_200.jpg"
            # Group 1: Scenario | Groups 2-5: x0, y0, x1, y1
            match = re.search(
                r"^(.*)_(\d+)_(\d+)_(\d+)_(\d+)\.(png|jpg|jpeg)$",
                img_path.name,
                re.IGNORECASE,
            )

            if match:
                scenario = match.group(1)
                x0 = int(match.group(2))
                y0 = int(match.group(3))
                x1 = int(match.group(4))
                y1 = int(match.group(5))

                # Append tuple: (expected box, image_path, scenario)
                test_cases.append((x0, y0, x1, y1, str(img_path), scenario))

    return test_cases


@pytest.mark.parametrize(
    "expected_x0, expected_y0, expected_x1, expected_y1, image_path, scenario",
    load_minimap_images(),
)
def test_minimap_bounding_box(
    expected_x0, expected_y0, expected_x1, expected_y1, image_path, scenario
):
    # Initialize your ONNX YOLO detector
    detector = MapDetector()
    image = cv2.imread(image_path)

    assert image is not None, f"Failed to load image for {scenario} at: {image_path}"

    # Get the prediction (assuming your method returns [x0, y0, x1, y1])
    predicted_box = detector.detect(image)

    assert predicted_box is not None, (
        f"Scenario: {scenario} | No bounding box detected!"
    )

    pred_x0, pred_y0, pred_x1, pred_y1 = predicted_box

    # YOLO predictions often flutter by a few pixels, so we use a tolerance
    TOLERANCE = 20

    # Check all four coordinates
    assert pred_x0 == pytest.approx(expected_x0, abs=TOLERANCE), (
        f"x0 mismatch in {scenario}"
    )
    assert pred_y0 == pytest.approx(expected_y0, abs=TOLERANCE), (
        f"y0 mismatch in {scenario}"
    )
    assert pred_x1 == pytest.approx(expected_x1, abs=TOLERANCE), (
        f"x1 mismatch in {scenario}"
    )
    assert pred_y1 == pytest.approx(expected_y1, abs=TOLERANCE), (
        f"y1 mismatch in {scenario}"
    )
