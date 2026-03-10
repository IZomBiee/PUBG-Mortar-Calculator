import re
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).parent.parent
FIXTURE_DIR = ROOT_DIR / "tests" / "fixtures" / "marks"

MAX_DIMENSION = 1920
JPEG_QUALITY = 50


def compress_and_scale_marks():
    if not FIXTURE_DIR.exists():
        FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {FIXTURE_DIR}. Please add images and run again.")
        return

    valid_extensions = ("*.png", "*.jpg", "*.jpeg")
    files = []
    for ext in valid_extensions:
        files.extend(FIXTURE_DIR.glob(ext))

    for img_path in files:
        # Matches: close_city_map_green_1643_964_959_1030.png
        match = re.search(
            r"^(.*)_(\d+)_(\d+)_(\d+)_(\d+)\.(png|jpg|jpeg)$",
            img_path.name,
            re.IGNORECASE,
        )

        if not match:
            print(
                f"Skipping '{img_path.name}' -> Doesn't match format 'prefix_px_py_mx_my.ext'"
            )
            continue

        prefix = match.group(1)
        px = int(match.group(2))
        py = int(match.group(3))
        mx = int(match.group(4))
        my = int(match.group(5))

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        scale = 1.0

        if w > MAX_DIMENSION or h > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Scale all four coordinate points
        new_px = int(round(px * scale))
        new_py = int(round(py * scale))
        new_mx = int(round(mx * scale))
        new_my = int(round(my * scale))

        new_filename = f"{prefix}_{new_px}_{new_py}_{new_mx}_{new_my}.jpg"
        new_filepath = FIXTURE_DIR / new_filename

        cv2.imwrite(str(new_filepath), img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])

        if img_path != new_filepath:
            img_path.unlink()

        print(f"Processed: '{img_path.name}' -> '{new_filename}' (Scale: {scale:.2f})")


if __name__ == "__main__":
    compress_and_scale_marks()
