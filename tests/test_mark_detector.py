import re
from pathlib import Path

import cv2
import pytest

# Adjust this import to match your project structure
from src.pubg_mortar_calculator.detectors import MarkDetector
from src.pubg_mortar_calculator.settings_loader import SettingsLoader as SL

FIXTURE_DIR = Path("tests/fixtures/marks")


def load_mark_images():
    """Extracts color and coordinates from filenames like 'map_green_1643_964_959_1030.jpg'"""
    test_cases = []
    if not FIXTURE_DIR.exists():
        return test_cases

    for img_path in FIXTURE_DIR.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            # Group 1: prefix | Group 2: color | Groups 3-6: px, py, mx, my
            # This looks for one of your supported colors exactly before the coordinates
            match = re.search(
                r"^(.*)_(orange|yellow|blue|green)_(\d+)_(\d+)_(\d+)_(\d+)\.(png|jpg|jpeg)$",
                img_path.name,
                re.IGNORECASE,
            )

            if match:
                scenario = match.group(1)
                color = match.group(2).lower()
                px = int(match.group(3))
                py = int(match.group(4))
                mx = int(match.group(5))
                my = int(match.group(6))

                test_cases.append((color, px, py, mx, my, str(img_path), scenario))

    return test_cases


def points_match(p1, p2, tolerance=5):
    """Returns True if point 1 and point 2 are within the tolerance distance."""
    # Handle cases where the detector returned None but we expected coordinates
    if p1 is None or p2 is None:
        return False
    return abs(p1[0] - p2[0]) <= tolerance and abs(p1[1] - p2[1]) <= tolerance


@pytest.mark.parametrize(
    "color, exp_px, exp_py, exp_mx, exp_my, image_path, scenario", load_mark_images()
)
def test_mark_detection(color, exp_px, exp_py, exp_mx, exp_my, image_path, scenario):
    image = cv2.imread(image_path)
    assert image is not None, f"Failed to load image for {scenario}"

    settings = SL()

    max_radius = settings.get(
        "map_detection_max_radius_slider"
    )  # Adjust key to match your SL

    # 1. Clean up the image (modifies in-place)
    MarkDetector.remove_danger_zones(image)

    # 2. Get the HSV mask using the color extracted from the filename
    hsv_mask = MarkDetector.get_hsv_mask(
        image,
        color=color,
        # You can add SL().get() for bluring_size and bluring_threshold here if needed
    )

    # 3. Get predictions
    pred_player, pred_mark = MarkDetector.get_mark_positions(hsv_mask, max_radius)

    assert pred_player is not None or pred_mark is not None, (
        f"Scenario: {scenario} ({color}) | Both predictions were None!"
    )

    expected_player = (exp_px, exp_py)
    expected_mark = (exp_mx, exp_my)

    # Order-Agnostic Logic: Does P1=Player and P2=Mark? OR P1=Mark and P2=Player?
    straight_match = points_match(pred_player, expected_player) and points_match(
        pred_mark, expected_mark
    )
    swapped_match = points_match(pred_player, expected_mark) and points_match(
        pred_mark, expected_player
    )

    # The test passes if EITHER configuration is true
    assert straight_match or swapped_match, (
        f"Scenario: {scenario} ({color}) | "
        f"Expected: {expected_player} & {expected_mark} | "
        f"Got: {pred_player} & {pred_mark}"
    )
