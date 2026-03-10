import re
from pathlib import Path

import cv2
import pytest

from src.pubg_mortar_calculator.detectors import GridDetector
from src.pubg_mortar_calculator.settings_loader import SettingsLoader as SL

# Point to your new fixtures directory
FIXTURE_DIR = Path("tests/fixtures/grids")


def load_test_images():
    """Dynamically loads test cases from the filenames in the fixtures folder."""
    test_cases = []

    # If the folder doesn't exist yet, return empty (pytest will warn you)
    if not FIXTURE_DIR.exists():
        return test_cases

    for img_path in FIXTURE_DIR.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            # Match filenames like "swamp_clear_288.jpg"
            match = re.search(
                r"^(.*)_(\d+)\.(png|jpg|jpeg)$", img_path.name, re.IGNORECASE
            )

            if match:
                scenario = match.group(1)  # e.g., "swamp_clear"
                expected_gap = float(match.group(2))  # e.g., 288.0

                # Append tuple: (expected_gap, image_path, scenario)
                test_cases.append((expected_gap, str(img_path), scenario))

    return test_cases


# Pytest automatically calls load_test_images() to get the list of parameters
@pytest.mark.parametrize("expected_gap, image_path, scenario", load_test_images())
def test_grid_gap(expected_gap, image_path, scenario):
    grid_detector = GridDetector()
    image = cv2.imread(image_path)

    assert image is not None, f"Failed to load image for {scenario} at: {image_path}"

    settings = SL()

    canny = grid_detector.get_canny_frame(
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

    assert calc_gap is not None, (
        f"Scenario: {scenario} | Image: {image_path} | "
        f"Predicted: None | Ground Truth: {expected_gap}"
    )

    assert calc_gap == pytest.approx(expected_gap, abs=2), (
        f"Scenario: {scenario} | Image: {image_path} | "
        f"Delta: {abs(calc_gap - expected_gap)} | "
        f"Predicted: {calc_gap} | Ground Truth: {expected_gap}"
    )
