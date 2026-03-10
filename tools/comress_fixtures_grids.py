import re
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).parent.parent
FIXTURE_DIR = ROOT_DIR / "tests" / "fixtures" / "grids"

# --- CONFIGURATION ---
MAX_DIMENSION = 1920  # Max width or height
JPEG_QUALITY = 50  # 0 to 100 (lower = smaller file size, but more blurry)


def compress_and_rename():
    if not FIXTURE_DIR.exists():
        print(f"Directory not found: {FIXTURE_DIR}")
        return

    # Look for all png, jpg, and jpeg files
    valid_extensions = ("*.png", "*.jpg", "*.jpeg")
    files = []
    for ext in valid_extensions:
        files.extend(FIXTURE_DIR.glob(ext))

    for img_path in files:
        # Match filenames like "swamp_clear_288.png" to extract the "288"
        match = re.search(r"^(.*)_(\d+)\.(png|jpg|jpeg)$", img_path.name, re.IGNORECASE)

        if not match:
            print(f"Skipping '{img_path.name}' -> Doesn't match format 'name_GAP.ext'")
            continue

        prefix = match.group(1)
        old_gap = float(match.group(2))

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

        # Calculate the new gap (rounded to nearest integer)
        new_gap = int(round(old_gap * scale))

        # Build the new filename and path
        new_filename = f"{prefix}_{new_gap}.jpg"
        new_filepath = FIXTURE_DIR / new_filename

        # Save as heavily compressed JPG
        cv2.imwrite(str(new_filepath), img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])

        # Delete the old file if the name or extension changed
        if img_path != new_filepath:
            img_path.unlink()

        print(f"Processed: '{img_path.name}' -> '{new_filename}' (Scale: {scale:.2f})")


if __name__ == "__main__":
    compress_and_rename()
