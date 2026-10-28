import cv2
import numpy as np

from ..utils import imgpr


def get_mark_positions(
    hsv_mask: np.ndarray,
    min_radius: float,
    max_radius: float,
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    contours = _find_contours(hsv_mask)

    player_cord = None
    mark_cord = None

    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)

        cx, cy = int(x), int(y)
        if min_radius < radius and radius < max_radius:
            if player_cord is None:
                player_cord = (cx, cy)

            elif mark_cord is None:
                mark_cord = (cx, int(cy + (radius)))

            else:
                break

    return (player_cord, mark_cord)


def get_all_positions(
    hsv_mask: np.ndarray,
) -> list[tuple[int, int, float]]:
    contours = _find_contours(hsv_mask)

    detections = []

    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)

        cx, cy = int(x), int(y)
        detections.append((cx, cy, radius))

    return detections


def draw_marks(
    bgr_image: np.ndarray,
    player_position: tuple[int, int] | None,
    mark_position: tuple[int, int] | None,
) -> np.ndarray:
    if player_position is not None:
        imgpr.draw_point(bgr_image, player_position, "Player", (255, 0, 0))
    if mark_position is not None:
        imgpr.draw_point(bgr_image, mark_position, "Mark", (0, 0, 255))
    return bgr_image


def remove_danger_zones(image: np.ndarray):
    height, width = image.shape[:2]

    imgpr.replace_area_with_black(
        image, (0, int(height * 0.83)), (int(width * 0.13), height)
    )
    imgpr.replace_area_with_black(
        image, (int(width * 0.75), int(height * 0.8)), (width, height)
    )
    imgpr.replace_area_with_black(
        image, (int(width * 0.8), 0), (width, int(height * 0.25))
    )
    imgpr.replace_area_with_black(
        image, (int(width * 0.3), int(height * 0.9)), (int(width * 0.7), height)
    )


def get_hsv_mask(
    bgr_image: np.ndarray,
    color: str,
    bluring_size: int = 9,
    bluring_threshold: int = 10,
) -> np.ndarray:
    hsv_frame = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_frame, *__color_to_hsv_range(color))

    mask = cv2.GaussianBlur(mask, (bluring_size, bluring_size), 7)

    _, mask = cv2.threshold(mask, bluring_threshold, 255, cv2.THRESH_BINARY)

    return mask


def get_roi_hsv_mask(
    bgr_image: np.ndarray,
    color: str,
    bluring_size: int = 41,
) -> np.ndarray:
    hsv_frame = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_frame, *__color_to_hsv_range(color))

    mask = cv2.GaussianBlur(mask, (bluring_size, bluring_size), 7)

    _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    return mask


def __color_to_hsv_range(color: str) -> tuple[np.ndarray, np.ndarray]:
    match color:
        case "orange":
            # hsv_min = (10, 106, 123)
            # hsv_max = (13, 238, 231)
            hsv_min = (10, 106, 123)
            hsv_max = (13, 238, 231)
        case "yellow":
            hsv_min = (23, 137, 163)
            hsv_max = (36, 255, 240)
        case "blue":
            hsv_min = (73, 65, 120)
            hsv_max = (117, 255, 255)
        case "green":
            hsv_min = (49, 101, 111)
            hsv_max = (80, 195, 219)
        case _:
            raise ValueError(f"There is no color {color}")
    return np.array(hsv_min, dtype=np.uint8), np.array(hsv_max, dtype=np.uint8)


def _find_contours(mask: np.ndarray) -> list:
    contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    return sorted_contours
