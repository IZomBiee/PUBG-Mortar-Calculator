from typing import Tuple

import cv2
import numpy as np

from pubg_mortar_calculator.logger import get_logger

from ..detectors import (
    GridDetector,
    MinimapDetector,
    MinimapType,
    YoloMarkDetector,
    hsv_mark_detector,
)
from ..utils import imgpr
from .models import GridSettings, MapData, MarkSettings, MinimapSettings

LOGGER = get_logger()


class MapProcessor:
    def __init__(self):
        self.grid_detector = GridDetector()

    def process(
        self,
        image: np.ndarray,
        minimap_detector: MinimapDetector | None,
        yolo_detector: YoloMarkDetector | None,
        grid_settings: GridSettings,
        mark_settings: MarkSettings,
        minimap_settings: MinimapSettings,
    ) -> Tuple[np.ndarray, MapData]:
        map_data = MapData()
        processed = image.copy()

        if minimap_settings.enabled and minimap_detector:
            map_data.minimap_type = minimap_detector.detect(processed)
            (processed, map_data.minimap_box) = self._cut_to_minimap(
                processed, map_data.minimap_type, minimap_settings
            )
        else:
            map_data.minimap_type = MinimapType.NO_MINIMAP

        canny = self.grid_detector.get_canny_image(
            processed, grid_settings.canny1, grid_settings.canny2
        )
        lines = self.grid_detector.get_normalized_lines(
            canny,
            grid_settings.line_threshold,
            grid_settings.line_gap,
            grid_settings.line_merge,
        )
        map_data.grid_gap = self.grid_detector.calculate_grid_gap(*lines)

        samples = []
        hsv_mask = None
        if map_data.minimap_type == MinimapType.NO_MINIMAP:
            hsv_mark_detector.remove_danger_zones(processed)
        if not mark_settings.use_yolo or yolo_detector is None:
            hsv_mask = hsv_mark_detector.get_hsv_mask(
                processed, mark_settings.color
            )
            map_data.player_position, map_data.mark_position = (
                hsv_mark_detector.get_mark_positions(
                    hsv_mask, mark_settings.min_radius, mark_settings.max_radius
                )
            )
        else:
            hsv_mask = hsv_mark_detector.get_roi_hsv_mask(
                processed, mark_settings.color,
            )
            positions = hsv_mark_detector.get_all_positions(hsv_mask)
            samples = yolo_detector.make_samples(processed, positions)
            map_data.player_position, map_data.mark_position = (
                yolo_detector.get_player_and_mark_pos(samples, mark_settings.color)
            )

        if map_data.player_position and map_data.mark_position and map_data.grid_gap:
            map_data.distance = self.grid_detector.get_distance(
                map_data.player_position, map_data.mark_position, map_data.grid_gap
            )

        if grid_settings.show_processed:
            processed = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
        elif mark_settings.show_processed and hsv_mask is not None:
            processed = cv2.cvtColor(hsv_mask, cv2.COLOR_GRAY2BGR)
            if mark_settings.use_yolo:
                for (x, y), image in samples:
                    h, w = image.shape[:2]
                    cv2.rectangle(processed, (x, y), (x + w, y + h), (0, 0, 255), 3)

        if grid_settings.draw_lines:
            self.grid_detector.draw_lines(processed, *lines)

        if mark_settings.draw_marks:
            hsv_mark_detector.draw_marks(
                processed, map_data.player_position, map_data.mark_position
            )

        if (
            map_data.mark_position
            and map_data.player_position
            and mark_settings.zoom_to_points
        ):
            processed = imgpr.cut_to_points(
                processed, map_data.mark_position, map_data.player_position
            )[0]

        LOGGER.info(f"Map Calculation Results: {map_data}")
        return processed, map_data

    def _cut_to_minimap(
        self, image: np.ndarray, minimap_type: MinimapType, settings: MinimapSettings
    ) -> Tuple[np.ndarray, Tuple[int, int, int, int] | None]:
        h, w = image.shape[:2]
        if minimap_type == MinimapType.NO_MINIMAP:
            return (image, None)
        offset = int(w * (settings.offset / 10000))
        size_scale = (
            settings.small_size / 5000
            if minimap_type == MinimapType.SMALL_MINIMAP
            else settings.large_size / 3000
        )
        x1, y1 = w - offset, h - offset
        x0, y0 = x1 - int(w * size_scale), y1 - int(w * size_scale)
        return imgpr.cut_to_points(image, (x0, y0), (x1, y1), 0)
