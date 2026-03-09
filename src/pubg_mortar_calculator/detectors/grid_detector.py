import math
from collections import Counter

import cv2
import numpy as np


class GridDetector:
    def __init__(self):
        self._normalize_multiplier = [1, 1]

    def get_normalized_lines(
        self,
        canny_image: np.ndarray,
        line_threshold: float,
        max_line_gap: float,
        line_merge_theshold: int,
    ) -> tuple[list, list]:
        normalized_canny_frame = self._normalize_frame(canny_image)

        side_size = normalized_canny_frame.shape[0]
        line_threshold = int(line_threshold * side_size)
        max_line_gap = int(max_line_gap * side_size)
        lines: np.ndarray | None = cv2.HoughLinesP(
            normalized_canny_frame,
            1,
            np.pi / 2,
            line_threshold,
            maxLineGap=max_line_gap,
        )

        if lines is None:
            return ([], [])

        processed_lines = []
        for line in lines:
            line = np.array(line[0])
            processed_lines.append(
                [
                    round(line[0] * self._normalize_multiplier[0]),
                    round(line[1] * self._normalize_multiplier[1]),
                    round(line[2] * self._normalize_multiplier[0]),
                    round(line[3] * self._normalize_multiplier[1]),
                ]
            )
        return self._separate_and_merge_lines(processed_lines, line_merge_theshold)

    @staticmethod
    def calculate_grid_gap(horizontal_lines: list, vertical_lines: list) -> int | None:
        horizontal_gaps = []
        vertical_gaps = []

        for i in range(0, len(horizontal_lines) - 1):
            x0, y0, x1, y1 = horizontal_lines[i]
            x2, y2, x3, y3 = horizontal_lines[i + 1]
            gap = int(abs(y0 - y2))
            horizontal_gaps.append(gap)

        for i in range(0, len(vertical_lines) - 1):
            x0, y0, x1, y1 = vertical_lines[i]
            x2, y2, x3, y3 = vertical_lines[i + 1]
            gap = int(abs(x0 - x2))
            vertical_gaps.append(gap)

        gaps = horizontal_gaps.copy()
        gaps.extend(vertical_gaps)

        if len(gaps):
            mode_gap = round(GridDetector.mode(gaps))
        else:
            mode_gap = None

        return mode_gap

    def _normalize_frame(self, frame: np.ndarray) -> np.ndarray:
        max_resolution = (
            frame.shape[0] if frame.shape[0] > frame.shape[1] else frame.shape[1]
        )
        self._normalize_multiplier = [
            frame.shape[1] / max_resolution,
            frame.shape[0] / max_resolution,
        ]
        frame = cv2.resize(
            frame, (max_resolution, max_resolution), interpolation=cv2.INTER_NEAREST
        )
        return frame

    @staticmethod
    def draw_lines(
        image: np.ndarray,
        vertical_lines: list,
        horizontal_lines: list,
        vertical_lines_color=(255, 0, 0),
        horizontal_lines_color=(0, 0, 255),
        trickness: float = 0.002,
    ) -> None:
        trickness = max(
            1, int(((image.shape[1] * trickness) + (image.shape[0] * trickness)) / 2)
        )

        for x0, y0, x1, y1 in vertical_lines:
            cv2.line(image, (x0, y0), (x1, y1), vertical_lines_color, trickness)

        for x0, y0, x1, y1 in horizontal_lines:
            cv2.line(image, (x0, y0), (x1, y1), horizontal_lines_color, trickness)

    @staticmethod
    def get_canny_frame(
        bgr_frame: np.ndarray, threshold1: int, threshold2: int, aperture_size: int = 3
    ) -> np.ndarray:
        gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        canny_frame = cv2.Canny(
            gray_frame, threshold1, threshold2, apertureSize=aperture_size
        )
        return canny_frame

    @staticmethod
    def mode(data):
        frequency = Counter(data)
        max_count = max(frequency.values())
        modes = [key for key, count in frequency.items() if count == max_count]
        return sum(modes) / len(modes) if len(modes) > 1 else modes[0]

    @staticmethod
    def get_distance(
        first_point: tuple[int, int], second_point: tuple[int, int], grid_gap: int
    ) -> float | None:
        if grid_gap == 0:
            return None
        delta_y = abs(first_point[0] - second_point[0]) / grid_gap * 100
        delta_x = abs(first_point[1] - second_point[1]) / grid_gap * 100
        return math.sqrt(delta_x**2 + delta_y**2)

    @staticmethod
    def _separate_and_merge_lines(
        lines: list[list[int]], threshold: int
    ) -> tuple[list, list]:
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x0, y0, x1, y1 = line
            if abs(x1 - x0) < abs(y1 - y0):
                vertical_lines.append(line)
            else:
                horizontal_lines.append(line)

        merged_horizontal_lines = GridDetector._merge_lines(
            horizontal_lines, index_to_merge=1, threshold=threshold
        )
        merged_vertical_lines = GridDetector._merge_lines(
            vertical_lines, index_to_merge=0, threshold=threshold
        )

        return merged_horizontal_lines, merged_vertical_lines

    @staticmethod
    def _merge_lines(
        lines: list[list[int]], index_to_merge: int, threshold: int
    ) -> list[list[int]]:
        if not lines:
            return []

        lines.sort(key=lambda x: x[index_to_merge])

        merged_lines = []
        current_cluster = [lines[0]]

        for current_line in lines[1:]:
            last_line = current_cluster[-1]

            dist = abs(current_line[index_to_merge] - last_line[index_to_merge])

            if dist < threshold:
                current_cluster.append(current_line)
            else:
                merged_lines.append(
                    GridDetector._average_cluster(current_cluster, index_to_merge)
                )
                current_cluster = [current_line]

        if current_cluster:
            merged_lines.append(
                GridDetector._average_cluster(current_cluster, index_to_merge)
            )

        return merged_lines

    @staticmethod
    def _average_cluster(cluster: list[list[int]], index_to_merge: int) -> list[int]:
        avg_pos = int(sum(line[index_to_merge] for line in cluster) / len(cluster))

        if index_to_merge == 1:
            min_x = min(min(line[0], line[2]) for line in cluster)
            max_x = max(max(line[0], line[2]) for line in cluster)
            return [min_x, avg_pos, max_x, avg_pos]

        else:
            min_y = min(min(line[1], line[3]) for line in cluster)
            max_y = max(max(line[1], line[3]) for line in cluster)
            return [avg_pos, min_y, avg_pos, max_y]
