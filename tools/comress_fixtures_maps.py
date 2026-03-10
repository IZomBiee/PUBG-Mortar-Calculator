import re
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).parent.parent
FIXTURE_DIR = ROOT_DIR / "tests" / "fixtures" / "maps"

# --- CONFIGURATION ---
MAX_DIMENSION = 1920  # Max width or height
JPEG_QUALITY = 50  # 0 to 100 (lower = smaller file size)


def compress_and_scale_minimaps():
    if not FIXTURE_DIR.exists():
        print(f"Directory not found: {FIXTURE_DIR}")
        return

    # Look for all png, jpg, and jpeg files
    valid_extensions = ("*.png", "*.jpg", "*.jpeg")
    files = []
    for ext in valid_extensions:
        files.extend(FIXTURE_DIR.glob(ext))

    for img_path in files:
        # Match filenames like "desert_zoom_10_20_150_200.png"
        # Group 1: prefix | Groups 2-5: x0, y0, x1, y1
        match = re.search(
            r"^(.*)_(\d+)_(\d+)_(\d+)_(\d+)\.(png|jpg|jpeg)$",
            img_path.name,
            re.IGNORECASE,
        )

        if not match:
            print(
                f"Skipping '{img_path.name}' -> Doesn't match format 'name_x0_y0_x1_y1.ext'"
            )
            continue

        prefix = match.group(1)
        x0 = int(match.group(2))
        y0 = int(match.group(3))
        x1 = int(match.group(4))
        y1 = int(match.group(5))

        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Skipping '{img_path.name}' -> Could not read file")
            continue

        h, w = img.shape[:2]
        scale = 1.0

        # Check if we need to resize
        if w > MAX_DIMENSION or h > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Scale the bounding box coordinates!
        new_x0 = int(round(x0 * scale))
        new_y0 = int(round(y0 * scale))
        new_x1 = int(round(x1 * scale))
        new_y1 = int(round(y1 * scale))

        # Build the new filename
        new_filename = f"{prefix}_{new_x0}_{new_y0}_{new_x1}_{new_y1}.jpg"
        new_filepath = FIXTURE_DIR / new_filename

        # Save as heavily compressed JPG
        cv2.imwrite(str(new_filepath), img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])

        # Delete the old file if the name or extension changed
        if img_path != new_filepath:
            img_path.unlink()

        print(f"Processed: '{img_path.name}' -> '{new_filename}' (Scale: {scale:.2f})")


if __name__ == "__main__":
    compress_and_scale_minimaps()
