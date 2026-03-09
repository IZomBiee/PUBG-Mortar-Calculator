import cv2
import numpy as np

from ..utils import imgpr


class MarkDetector:
    @staticmethod
    def get_mark_positions(
        hsv_mask: np.ndarray, max_radius: float
    ) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
        contours = MarkDetector._find_contours(hsv_mask)

        player_cord = None
        mark_cord = None

        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)

            cx, cy = int(x), int(y)
            if radius < max_radius:
                if player_cord is None:
                    player_cord = (cx, cy)

                elif mark_cord is None:
                    mark_cord = (cx, int(cy + (radius)))

                else:
                    break

        return (player_cord, mark_cord)

    @staticmethod
    def get_hsv_mask(
        bgr_frame: np.ndarray,
        color: str,
        bluring_size: int = 5,
        bluring_threshold: int = 15,
    ) -> np.ndarray:
        hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv_frame, *MarkDetector._color_to_hsv_range(color))

        mask = cv2.GaussianBlur(mask, (bluring_size, bluring_size), 7)

        ret, mask = cv2.threshold(mask, bluring_threshold, 255, cv2.THRESH_BINARY)

        return mask

    @staticmethod
    def draw_marks(
        image: np.ndarray,
        player_position: tuple[int, int] | None,
        mark_position: tuple[int, int] | None,
    ) -> np.ndarray:
        if player_position is not None:
            imgpr.draw_point(image, player_position, "Player", (255, 0, 0))
        if mark_position is not None:
            imgpr.draw_point(image, mark_position, "Mark", (0, 0, 255))
        return image

    @staticmethod
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

    @staticmethod
    def _color_to_hsv_range(color: str) -> tuple[np.ndarray, np.ndarray]:
        match color:
            case "orange":
                hsv_min = (10, 106, 123)
                hsv_max = (13, 238, 231)
            case "yellow":
                hsv_min = (23, 137, 163)
                hsv_max = (36, 255, 240)
            case "blue":
                hsv_min = (67, 70, 106)
                hsv_max = (110, 210, 231)
            case "green":
                hsv_min = (49, 101, 111)
                hsv_max = (80, 195, 219)
            case _:
                raise ValueError(f"There is no color {color}")
        return np.array(hsv_min, dtype=np.uint8), np.array(hsv_max, dtype=np.uint8)

    @staticmethod
    def _find_contours(mask: np.ndarray) -> list:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

        return sorted_contours
