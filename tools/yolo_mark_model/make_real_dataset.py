import math
import random
import shutil
from pathlib import Path

import cv2

from pubg_mortar_calculator.detectors import hsv_mark_detector
from pubg_mortar_calculator.detectors.yolo_mark_detector import YoloMarkDetector

from .make_syn_dataset import (
    Annotation,
    check_clarity_and_crop,
    get_annotations_from_file,
    write_annotations,
)

DATASET_PATH = Path(r"A:\Datasets\PUBG\original")
OUTPUT_PATH = Path(__file__).resolve().parents[0] / "mark_dataset"
OUTPUT_PATH.mkdir(exist_ok=True)
CLASSE_IDS = [1, 2, 3, 4, 5, 6, 7, 8]
MIN_CLEARITY = 0.5
BACKGROUND_PERCENT = 10.0
MIN_DISTANCE = 20

if __name__ == "__main__":
    total_positives = 0
    total_negatives = 0

    for file in DATASET_PATH.iterdir():
        if file.name.endswith("txt"):
            if "classes" in file.name:
                shutil.copy(file, OUTPUT_PATH / file.name)
            continue

        print(file)

        image = cv2.imread(str(file))
        if image is None:
            exit(f"Could not read {file} as image")

        annotation_path = file.with_suffix(".txt")
        annotations = (
            get_annotations_from_file(annotation_path)
            if annotation_path.exists()
            else []
        )

        image_height, image_width = image.shape[:2]

        map_box = None
        for annotation in annotations:
            if annotation.id == 0:
                x0 = int(annotation.x * image_width)
                y0 = int(annotation.y * image_height)
                map_box = (
                    x0,
                    y0,
                    x0 + int(annotation.w * image_width),
                    y0 + int(annotation.h * image_height),
                )
                break

        if map_box is not None:
            mx0, my0, mx1, my1 = map_box
            image = image[my0:my1, mx0:mx1]
            map_w = mx1 - mx0
            map_h = my1 - my0

            adjusted_annotations = []
            for ann in annotations:
                if ann.id not in CLASSE_IDS:
                    continue
                res = check_clarity_and_crop(
                    ann, image_width, image_height, mx0, my0, map_w, map_h, 1.0
                )
                if res is not None:
                    adjusted_annotations.append(res[0])

            annotations = adjusted_annotations
            image_height, image_width = image.shape[:2]
        else:
            hsv_mark_detector.remove_danger_zones(image)

        candidates = []

        for color in ["yellow", "green", "blue", "orange"]:
            mask = hsv_mark_detector.get_roi_hsv_mask(image, color)
            points = hsv_mark_detector.get_all_positions(mask)
            samples = YoloMarkDetector.make_samples(image, points)

            for offset, crop in samples:
                cutted_h, cutted_w = crop.shape[:2]
                crop_x0, crop_y0 = offset[0], offset[1]

                size = max(cutted_h, cutted_w)
                size = min(size, image_width, image_height)
                if size <= 0:
                    continue

                crop_x0 = max(0, min(crop_x0, image_width - size))
                crop_y0 = max(0, min(crop_y0, image_height - size))
                square_crop = image[crop_y0 : crop_y0 + size, crop_x0 : crop_x0 + size]

                if (
                    square_crop.shape[0] != square_crop.shape[1]
                    or square_crop.shape[0] == 0
                ):
                    continue

                new_annotations = []
                for other_annotation in annotations:
                    if other_annotation.id not in CLASSE_IDS:
                        continue

                    result = check_clarity_and_crop(
                        other_annotation,
                        image_width,
                        image_height,
                        crop_x0,
                        crop_y0,
                        size,
                        size,
                        MIN_CLEARITY,
                    )

                    if result is not None:
                        new_ann, _ = result
                        new_annotations.append(new_ann)

                candidates.append(
                    (crop_x0, crop_y0, size, square_crop, new_annotations)
                )

        candidates.sort(key=lambda c: len(c[4]), reverse=True)

        filtered_candidates = []
        for c_x0, c_y0, c_size, c_crop, c_anns in candidates:
            c_cx = c_x0 + c_size / 2.0
            c_cy = c_y0 + c_size / 2.0

            is_duplicate = False
            for f_x0, f_y0, f_size, _, _ in filtered_candidates:
                f_cx = f_x0 + f_size / 2.0
                f_cy = f_y0 + f_size / 2.0
                if math.hypot(c_cx - f_cx, c_cy - f_cy) < MIN_DISTANCE:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered_candidates.append((c_x0, c_y0, c_size, c_crop, c_anns))

        positives = [c for c in filtered_candidates if len(c[4]) > 0]
        negatives = [c for c in filtered_candidates if len(c[4]) == 0]

        for c_x0, c_y0, _, c_crop, c_anns in positives:
            new_annotation_path = (
                OUTPUT_PATH / f"{file.with_suffix('').name}^{c_x0}_{c_y0}.txt"
            )
            new_image_path = new_annotation_path.with_suffix(".png")
            write_annotations(new_annotation_path, c_anns)
            cv2.imwrite(str(new_image_path), c_crop)
            total_positives += 1

        if total_positives > 0:
            target_negatives = round(total_positives * (BACKGROUND_PERCENT / 100.0))
            allowed_negatives = max(0, target_negatives - total_negatives)
        else:
            allowed_negatives = round(len(negatives) * (BACKGROUND_PERCENT / 100.0))

        allowed_negatives = min(allowed_negatives, len(negatives))
        if allowed_negatives > 0:
            selected_negatives = random.sample(negatives, allowed_negatives)
            for c_x0, c_y0, _, c_crop, c_anns in selected_negatives:
                new_annotation_path = (
                    OUTPUT_PATH / f"{file.with_suffix('').name}^{c_x0}_{c_y0}.txt"
                )
                new_image_path = new_annotation_path.with_suffix(".png")
                write_annotations(new_annotation_path, c_anns)
                cv2.imwrite(str(new_image_path), c_crop)
                total_negatives += 1
