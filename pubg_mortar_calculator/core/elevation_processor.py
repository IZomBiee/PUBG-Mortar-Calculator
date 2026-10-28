from typing import Tuple

import cv2
import numpy as np

from pubg_mortar_calculator.core.elevation_tools import ElevationTools
from pubg_mortar_calculator.core.models import (
    ElevationData,
    ElevationSettings,
    MarkSettings,
)
from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.logger import get_logger
from pubg_mortar_calculator.utils import imgpr

LOGGER = get_logger()


class ElevationProcessor:
    def process(
        self,
        image: np.ndarray,
        distance: float | None,
        mortar_distances: list[int],
        elevation_settings: ElevationSettings,
        mark_settings: MarkSettings,
    ) -> Tuple[np.ndarray, ElevationData]:
        data = ElevationData()
        processed = image.copy()

        cut_y = int(processed.shape[0] * 0.1)
        imgpr.replace_area_with_black(processed, (0, 0), (processed.shape[1], cut_y))

        data.center_position = imgpr.get_center_point(processed)
        cutted_img, (x_start, x_end) = imgpr.cut_x_line(
            processed, data.center_position[0], 0.02
        )
        cutted_center = imgpr.get_center_point(cutted_img)

        hsv_mask = hsv_mark_detector.get_hsv_mask(
            cutted_img, mark_settings.color, 19, 1
        )
        data.mark_position = hsv_mark_detector.get_mark_positions(
            hsv_mask, mark_settings.min_radius, mark_settings.max_radius
        )[0]

        if data.mark_position and distance:
            data.elevation = ElevationTools.get_elevation(
                data.center_position[1],
                data.mark_position[1],
                elevation_settings.fov,
                distance,
            )
            data.elevated_distance = ElevationTools.get_elevated_distance(
                distance, data.elevation
            )

        if data.elevated_distance is not None:
            if data.elevated_distance < 120:
                data.mortar_elevated_distance = "Too close"
            elif data.elevated_distance > 705:
                data.mortar_elevated_distance = "Too far"
            else:
                data.mortar_elevated_distance = (
                    ElevationTools.calculate_mortar_distance(
                        data.elevated_distance, mortar_distances
                    )
                )

        if elevation_settings.draw_processed:
            cutted_img = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)

        if elevation_settings.draw_points:
            cv2.circle(cutted_img, cutted_center, 2, (0, 255, 0), 5)
            if data.mark_position:
                cv2.arrowedLine(
                    cutted_img, cutted_center, data.mark_position, (0, 255, 0), 3
                )
                cv2.circle(cutted_img, data.mark_position, 2, (0, 255, 0), 5)

        data.x_start = x_start

        LOGGER.info(f"Elevation Calculation Results: {data}")
        return cutted_img[cut_y:], data
