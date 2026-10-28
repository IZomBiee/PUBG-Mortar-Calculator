from enum import Enum

import cv2
import numpy as np

from pubg_mortar_calculator.detectors.onnx_classificator import ONNXClassificator
from pubg_mortar_calculator.utils import paths


class MinimapType(Enum):
    NO_MINIMAP = 0
    SMALL_MINIMAP = 1
    LARGE_MINIMAP = 2


class MinimapDetector(ONNXClassificator):
    def __init__(self) -> None:
        super().__init__(paths.map_detection_model())
        meta = self.session.get_modelmeta().custom_metadata_map
        self.cut_factor = float(meta.get("cut_factor", 0.35))

    def _basic_preprocess(self, bgr_image: np.ndarray) -> np.ndarray:
        height, width = bgr_image.shape[:2]
        size = round(width * self.cut_factor)
        bgr_image = bgr_image[height - size : height, width - size : width]
        return super()._basic_preprocess(bgr_image)

    def detect(self, image: np.ndarray) -> MinimapType:
        return MinimapType(super().detect(image))


if __name__ == "__main__":
    from matplotlib import pyplot as plt
    
    detector = MinimapDetector()

    image = cv2.imread(paths.map_preview())
    image = cv2.imread(r"tests\fixtures\TslGame_bDodaZ2l4Y.webp")
    if image is None:
        exit(f"Cannot load map preview image from {paths.map_preview()}!")

    probs = detector._get_probs(image)
    image = detector._basic_preprocess(image)

    plt.figure(figsize=(5, 5))
    plt.imshow(image)
    plt.title(
        f"Pred: {[round(float(i), 3) for i in probs]}",
        fontsize=12,
        fontweight="bold",
        color="green",
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()
