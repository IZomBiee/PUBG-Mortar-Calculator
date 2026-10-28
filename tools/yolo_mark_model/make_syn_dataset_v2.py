import os
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
import cv2

DATASET_PATH = Path(r"A:\Datasets\PUBG\original")
OUTPUT_PATH = Path(__file__).resolve().parent / "mark_dataset"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

TARGET_SIZE = 160
BASE_HEIGHT = 1080.0
BASE_ASPECT = 16.0 / 9.0

CLASS_IDS = {1, 2, 3, 4, 5, 6, 7, 8}
MIN_CLARITY = 0.5
OFFSET_MAX_PX = 35
BACKGROUND_RATIO = 0.15


@dataclass
class Annotation:
    id: int
    x: float
    y: float
    w: float
    h: float


def get_annotations_from_file(file_path: Path) -> list[Annotation]:
    data = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            data.append(
                Annotation(
                    id=int(parts[0]),
                    x=float(parts[1]),
                    y=float(parts[2]),
                    w=float(parts[3]),
                    h=float(parts[4]),
                )
            )
    return data


def write_annotations(path: Path, annotations: list[Annotation]):
    with open(path, "w") as file:
        for ann in annotations:
            file.write(f"{ann.id} {ann.x:.6f} {ann.y:.6f} {ann.w:.6f} {ann.h:.6f}\n")


def calculate_crop_dimensions(image_w: int, image_h: int, target_size: int = TARGET_SIZE) -> tuple[int, int]:
    scale_y = image_h / BASE_HEIGHT
    aspect = image_w / image_h
    aspect_ratio_factor = aspect / BASE_ASPECT

    crop_h = int(round(target_size * scale_y))
    if aspect < BASE_ASPECT:
        crop_w = int(round(target_size * scale_y * aspect_ratio_factor))
    else:
        crop_w = crop_h

    crop_w = min(image_w, max(32, crop_w))
    crop_h = min(image_h, max(32, crop_h))
    return crop_w, crop_h


def evaluate_bbox_overlap(
    ann: Annotation,
    img_w: int,
    img_h: int,
    x0: int,
    y0: int,
    crop_w: int,
    crop_h: int,
    min_clarity: float,
) -> Annotation | None:
    abs_cx = ann.x * img_w
    abs_cy = ann.y * img_h
    abs_w = ann.w * img_w
    abs_h = ann.h * img_h

    left = abs_cx - abs_w / 2.0
    right = abs_cx + abs_w / 2.0
    top = abs_cy - abs_h / 2.0
    bottom = abs_cy + abs_h / 2.0

    inter_left = max(float(x0), left)
    inter_right = min(float(x0 + crop_w), right)
    inter_top = max(float(y0), top)
    inter_bottom = min(float(y0 + crop_h), bottom)

    inter_w = max(0.0, inter_right - inter_left)
    inter_h = max(0.0, inter_bottom - inter_top)
    inter_area = inter_w * inter_h
    orig_area = abs_w * abs_h

    if orig_area <= 0 or (inter_area / orig_area) < min_clarity:
        return None

    crop_l = inter_left - x0
    crop_r = inter_right - x0
    crop_t = inter_top - y0
    crop_b = inter_bottom - y0

    new_x = (crop_l + crop_r) / (2.0 * crop_w)
    new_y = (crop_t + crop_b) / (2.0 * crop_h)
    new_w = (crop_r - crop_l) / float(crop_w)
    new_h = (crop_b - crop_t) / float(crop_h)

    return Annotation(ann.id, new_x, new_y, new_w, new_h)


def generate_dataset():
    files = [f for f in DATASET_PATH.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg"}]

    for file in files:
        classes_txt = file.parent / "classes.txt"
        if classes_txt.exists() and not (OUTPUT_PATH / "classes.txt").exists():
            shutil.copy(classes_txt, OUTPUT_PATH / "classes.txt")

        image = cv2.imread(str(file))
        if image is None:
            continue

        img_h, img_w = image.shape[:2]
        ann_path = file.with_suffix(".txt")
        annotations = get_annotations_from_file(ann_path) if ann_path.exists() else []
        valid_anns = [a for a in annotations if a.id in CLASS_IDS]

        crop_w, crop_h = calculate_crop_dimensions(img_w, img_h, TARGET_SIZE)

        for i, target_ann in enumerate(valid_anns):
            cx = int(round(target_ann.x * img_w))
            cy = int(round(target_ann.y * img_h))

            jitter_x = random.randint(-OFFSET_MAX_PX, OFFSET_MAX_PX)
            jitter_y = random.randint(-OFFSET_MAX_PX, OFFSET_MAX_PX)

            x0 = max(0, min(cx - crop_w // 2 + jitter_x, img_w - crop_w))
            y0 = max(0, min(cy - crop_h // 2 + jitter_y, img_h - crop_h))

            patch = image[y0 : y0 + crop_h, x0 : x0 + crop_w]
            resized_patch = cv2.resize(
                patch, 
                (TARGET_SIZE, TARGET_SIZE), 
                interpolation=cv2.INTER_AREA if crop_h >= TARGET_SIZE else cv2.INTER_LINEAR
            )

            crop_annotations = []
            for ann in valid_anns:
                res = evaluate_bbox_overlap(ann, img_w, img_h, x0, y0, crop_w, crop_h, MIN_CLARITY)
                if res is not None:
                    crop_annotations.append(res)

            sample_stem = f"{file.stem}_m{i}_{x0}_{y0}"
            cv2.imwrite(str(OUTPUT_PATH / f"{sample_stem}.png"), resized_patch)
            write_annotations(OUTPUT_PATH / f"{sample_stem}.txt", crop_annotations)

        num_bg = int(round(len(valid_anns) * BACKGROUND_RATIO))
        for bg_idx in range(max(1, num_bg)):
            bg_x0 = random.randint(0, max(0, img_w - crop_w))
            bg_y0 = random.randint(0, max(0, img_h - crop_h))

            has_marker = False
            for ann in valid_anns:
                if evaluate_bbox_overlap(ann, img_w, img_h, bg_x0, bg_y0, crop_w, crop_h, min_clarity=0.1) is not None:
                    has_marker = True
                    break

            if not has_marker:
                bg_patch = image[bg_y0 : bg_y0 + crop_h, bg_x0 : bg_x0 + crop_w]
                resized_bg = cv2.resize(
                    bg_patch, 
                    (TARGET_SIZE, TARGET_SIZE), 
                    interpolation=cv2.INTER_AREA if crop_h >= TARGET_SIZE else cv2.INTER_LINEAR
                )
                bg_stem = f"{file.stem}_bg{bg_idx}_{bg_x0}_{bg_y0}"
                cv2.imwrite(str(OUTPUT_PATH / f"{bg_stem}.png"), resized_bg)
                write_annotations(OUTPUT_PATH / f"{bg_stem}.txt", [])


if __name__ == "__main__":
    generate_dataset()