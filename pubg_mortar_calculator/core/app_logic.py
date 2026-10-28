import cv2
import numpy as np

from pubg_mortar_calculator.core.app_overlay import *
from pubg_mortar_calculator.core.dictor_manager import DictorManager
from pubg_mortar_calculator.core.elevation_processor import ElevationProcessor
from pubg_mortar_calculator.core.map_processor import MapProcessor
from pubg_mortar_calculator.core.models import (
    DictorSettings,
    ElevationData,
    ElevationSettings,
    GeneralSettings,
    GridSettings,
    MapData,
    MarkSettings,
    MinimapSettings,
    OverlaySettings,
)
from pubg_mortar_calculator.detectors import MinimapDetector, YoloMarkDetector
from pubg_mortar_calculator.logger import get_logger
from pubg_mortar_calculator.utils import paths

from pubg_mortar_calculator.core.storage import ImageStorage

LOGGER = get_logger()


class AppLogic:
    def __init__(self, dictor_rate: int = 200, dictor_volume: float = 1.0):
        self.map_image: np.ndarray | None = None
        self.elevation_image: np.ndarray | None = None
        self.map_data = MapData()
        self.elevation_data = ElevationData()

        with open(paths.mortar_distances(), "r") as f:
            self.mortar_distances = [int(line) for line in f.readlines()]

        self.map_processor = MapProcessor()
        self.elevation_processor = ElevationProcessor()

        self.minimap_detector = (
            MinimapDetector() if paths.map_detection_model().exists() else None
        )
        self.yolo_mark_detector = (
            YoloMarkDetector() if paths.mark_detection_model().exists() else None
        )

        self.dictor = DictorManager(dictor_rate, dictor_volume)
        self.dictor.start()

        self.map_image, self.elevation_image = ImageStorage.load_cached_images()

    def set_map_image(
        self,
        image: np.ndarray,
        grid_settings: GridSettings,
        mark_settings: MarkSettings,
        minimap_settings: MinimapSettings,
        dictor_settings: DictorSettings,
        general_settings: GeneralSettings,
        combat: bool = True,
    ) -> tuple[np.ndarray, MapData]:
        self.map_image = image
        processed_img, self.map_data = self.map_processor.process(
            self.map_image,
            self.minimap_detector,
            self.yolo_mark_detector,
            grid_settings,
            mark_settings,
            minimap_settings,
        )
        ImageStorage.save_map(self.map_image, combat and general_settings.debug_mode)

        if dictor_settings.enabled and combat:
            self.dictor.add(self.map_data.distance)

        return processed_img, self.map_data

    def set_elevation_image(
        self,
        image: np.ndarray,
        elevation_settings: ElevationSettings,
        mark_settings: MarkSettings,
        dictor_settings: DictorSettings,
        general_settings: GeneralSettings,
        combat: bool = True,
    ) -> tuple[np.ndarray, ElevationData]:
        self.elevation_image = image
        processed_img, self.elevation_data = self.elevation_processor.process(
            self.elevation_image,
            self.map_data.distance,
            self.mortar_distances,
            elevation_settings,
            mark_settings,
        )
        ImageStorage.save_elevation(
            self.elevation_image, combat and general_settings.debug_mode
        )

        if dictor_settings.enabled and combat:
            self.dictor.add(self.elevation_data.mortar_elevated_distance)

        return processed_img, self.elevation_data

    def load_image(self) -> None | np.ndarray:
        image_path = paths.get_image()
        if image_path is None:
            return

        image = cv2.imread(image_path)
        if image is None:
            return

        return image

    def draw_to_overlay(
        self, overlay: AppOverlay | None, overlay_settings: OverlaySettings
    ):
        if overlay_settings.enabled and overlay is not None:
            overlay.add_command(Clear())
            if overlay_settings.draw_borders:
                overlay.add_command(DrawBorders())

            scale = overlay_settings.scale / 100

            (x0, y0, x1, y1) = 0, 0, 0, 0
            if self.map_data.minimap_box is not None and overlay_settings.draw_minimap:
                (x0, y0, x1, y1) = self.map_data.minimap_box
                overlay.add_command(
                    CreateRect(
                        int(x0 / scale),
                        int(y0 / scale),
                        int(x1 / scale),
                        int(y1 / scale),
                    )
                )

            def fmt(val, precision=".1f"):
                return "None" if val is None else f"{val:{precision}}"

            text_to_display = [
                f"Distance: {fmt(self.map_data.distance)}",
                f"Mortar Distance: {self.elevation_data.mortar_elevated_distance}",
                f"Elevation: {fmt(self.elevation_data.elevation)}",
                f"Grid gap: {self.map_data.grid_gap}",
            ]

            y = 30
            for text in text_to_display:
                overlay.add_command(CreateText(text, 20, y, "red", 20))
                y += 30

            if overlay_settings.draw_map_marks:
                mark_position = self.map_data.mark_position
                if mark_position is not None:
                    mark_position = (
                        int((mark_position[0] + x0) / scale),
                        int((mark_position[1] + y0) / scale),
                    )
                    overlay.add_command(
                        CreateCircle(
                            mark_position[0], mark_position[1], 5, border_color="red"
                        )
                    )

                player_position = self.map_data.player_position
                if player_position is not None:
                    player_position = (
                        int((player_position[0] + x0) / scale),
                        int((player_position[1] + y0) / scale),
                    )
                    overlay.add_command(
                        CreateCircle(
                            player_position[0],
                            player_position[1],
                            5,
                            border_color="blue",
                        )
                    )

                if player_position is not None and mark_position is not None:
                    overlay.add_command(
                        CreateLine(
                            mark_position[0],
                            mark_position[1],
                            player_position[0],
                            player_position[1],
                            3,
                            "green",
                        )
                    )

            if (
                overlay_settings.draw_elevation_marks
                and self.elevation_data.mark_position is not None
                and self.elevation_data.center_position is not None
            ):
                overlay.add_command(
                    CreateCircle(
                        int(
                            (
                                self.elevation_data.mark_position[0]
                                + self.elevation_data.x_start
                            )
                            / scale
                        ),
                        int(self.elevation_data.mark_position[1] / scale),
                        5,
                        border_color="yellow",
                    )
                )
                overlay.add_command(
                    CreateLine(
                        int(
                            (
                                self.elevation_data.mark_position[0]
                                + self.elevation_data.x_start
                            )
                            / scale
                        ),
                        int(self.elevation_data.mark_position[1] / scale),
                        int(self.elevation_data.center_position[0] / scale),
                        int(self.elevation_data.center_position[1] / scale),
                        2,
                    )
                )
