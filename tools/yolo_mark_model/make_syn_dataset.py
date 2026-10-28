import shutil
from dataclasses import dataclass
from pathlib import Path
import random
import cv2

DATASET_PATH = Path(r"A:\Datasets\PUBG\original")
OUTPUT_PATH = Path(__file__).resolve().parents[0] / "mark_dataset"
OUTPUT_PATH.mkdir(exist_ok=True)
MARGINS = [1.5]
CLASSE_IDS = [1, 2, 3, 4, 5, 6, 7, 8]
OFFSET_FACTOR = 0.4
MIN_CLEARITY = 0.5

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
        for line in file.readlines():
            slices = line.split(" ")
            if len(slices) < 5:
                continue

            class_id = int(slices[0])
            class_x = float(slices[1])
            class_y = float(slices[2])
            class_w = float(slices[3])
            class_h = float(slices[4])
            data.append(Annotation(class_id, class_x, class_y, class_w, class_h))
    return data


def write_annotations(path: Path, annotations: list[Annotation]):
    with open(path, "w") as file:
        for annotation in annotations:
            file.write(
                f"{annotation.id} {annotation.x} {annotation.y} {annotation.w} {annotation.h}\n"
            )


def check_clarity_and_crop(
    annotation: Annotation,
    image_w: int,
    image_h: int,
    crop_x0: int,
    crop_y0: int,
    cutted_w: int,
    cutted_h: int,
    min_clarity: float,
):
    orig_x = annotation.x * image_w
    orig_y = annotation.y * image_h
    orig_w = annotation.w * image_w
    orig_h = annotation.h * image_h

    left = orig_x - orig_w / 2
    right = orig_x + orig_w / 2
    top = orig_y - orig_h / 2
    bottom = orig_y + orig_h / 2

    inter_left = max(crop_x0, left)
    inter_right = min(crop_x0 + cutted_w, right)
    inter_top = max(crop_y0, top)
    inter_bottom = min(crop_y0 + cutted_h, bottom)

    inter_w = max(0.0, inter_right - inter_left)
    inter_h = max(0.0, inter_bottom - inter_top)
    inter_area = inter_w * inter_h
    orig_area = orig_w * orig_h

    if orig_area == 0 or (inter_area / orig_area) < min_clarity:
        return None

    crop_l = inter_left - crop_x0
    crop_r = inter_right - crop_x0
    crop_t = inter_top - crop_y0
    crop_b = inter_bottom - crop_y0

    new_x = (crop_l + crop_r) / 2 / cutted_w
    new_y = (crop_t + crop_b) / 2 / cutted_h
    new_w = (crop_r - crop_l) / cutted_w
    new_h = (crop_b - crop_t) / cutted_h

    bbox_coords = (round(crop_l), round(crop_t), round(crop_r), round(crop_b))
    new_ann = Annotation(annotation.id, new_x, new_y, new_w, new_h)

    return new_ann, bbox_coords


if __name__ == "__main__":
    for file in DATASET_PATH.iterdir():
        if file.name.endswith("txt"):
            if "classes" in file.name:
                shutil.copy(file, OUTPUT_PATH / file.name)
            continue

        print(file)
        
        image = cv2.imread(file)
        if image is None:
            exit(f"Could not read {file} as image")
        image_height, image_width = image.shape[:2]

        annotation_path = file.with_suffix(".txt")
        if annotation_path.exists():
            annotations = get_annotations_from_file(annotation_path)
        else:
            annotations = []

        for annotation in annotations:
            if not annotation.id in CLASSE_IDS:
                continue

            x = round(annotation.x * image_width)
            y = round(annotation.y * image_height)
            w = round(annotation.w * image_width)
            h = round(annotation.h * image_height)

            for margin in MARGINS:
                margin = round(max(w, h) * margin)

                offset_x = round(
                    margin * random.uniform(-OFFSET_FACTOR, OFFSET_FACTOR)
                )
                offset_y = round(
                    margin * random.uniform(-OFFSET_FACTOR, OFFSET_FACTOR)
                )

                image_x0 = max(0, x - margin + offset_x)
                image_y0 = max(0, y - margin + offset_y)
                image_x1 = min(image_width, image_x0 + margin * 2)
                image_y1 = min(image_height, image_y0 + margin * 2)

                cutted_image = image[image_y0:image_y1, image_x0:image_x1].copy()
                cutted_h, cutted_w = cutted_image.shape[:2]
                new_annotations = []

                for other_annotation in annotations:
                    if other_annotation.id not in CLASSE_IDS:
                        continue

                    result = check_clarity_and_crop(
                        other_annotation,
                        image_width,
                        image_height,
                        image_x0,
                        image_y0,
                        cutted_w,
                        cutted_h,
                        MIN_CLEARITY,
                    )
                    if result is None:
                        continue

                    new_ann, (x1, y1, x2, y2) = result
                    # cv2.rectangle(
                    #     cutted_image, (x1, y1), (x2, y2), (255, 0, 255), 1
                    # )
                    new_annotations.append(new_ann)

                new_annotation_name = Path(
                    f"{file.with_suffix('').name}^{margin}_{x}_{y}"
                )
                new_annotation_path = (
                    OUTPUT_PATH
                    / f"{file.with_suffix('').name}^{margin}_{x}_{y}.txt"
                )
                new_image_path = new_annotation_path.with_suffix(".png")

                # cv2.imshow("A", cutted_image)
                # cv2.waitKey(0)

                write_annotations(new_annotation_path, new_annotations)
                cv2.imwrite(new_image_path, cutted_image)