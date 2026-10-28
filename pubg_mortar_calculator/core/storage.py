import shutil
from datetime import datetime

import cv2
import numpy as np

from pubg_mortar_calculator.logger import get_logger
from pubg_mortar_calculator.utils import paths

LOGGER = get_logger()


class ImageStorage:
    @staticmethod
    def load_cached_images() -> tuple[np.ndarray | None, np.ndarray | None]:
        map_img = (
            cv2.imread(str(paths.map_preview()))
            if paths.map_preview().exists()
            else None
        )
        elev_img = (
            cv2.imread(str(paths.elevation_preview()))
            if paths.elevation_preview().exists()
            else None
        )
        return map_img, elev_img

    @staticmethod
    def save_map(image: np.ndarray | None, debug_mode: bool):
        if image is None:
            return
        cv2.imwrite(str(paths.map_preview()), image)
        if debug_mode:
            target = (
                paths.debug_files()
                / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_map')}.png"
            )
            shutil.copy2(paths.map_preview(), target)
            LOGGER.info(f"Map preview saved to {target}")

    @staticmethod
    def save_elevation(image: np.ndarray | None, debug_mode: bool):
        if image is None:
            return
        cv2.imwrite(str(paths.elevation_preview()), image)
        if debug_mode:
            target = (
                paths.debug_files()
                / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_elevation')}.png"
            )
            shutil.copy2(paths.elevation_preview(), target)
            LOGGER.info(f"Elevation preview saved to {target}")
