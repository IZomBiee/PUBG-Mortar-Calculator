from pathlib import Path

import cv2
import numpy as np

ROOT_DIR = Path(__file__).parent.parent
FIXTURE_DIR = ROOT_DIR / "tests" / "fixtures"


def compress_fixtures():
    if not FIXTURE_DIR.exists():
        print(f"Directory not found: {FIXTURE_DIR}")
        return

    files = sorted(FIXTURE_DIR.glob("*.png"))
    if not files:
        print("No .png files found in fixtures directory.")
        return

    total_orig_size = 0
    total_webp_size = 0

    print(f"Processing {len(files)} files...\n")

    for img_path in files:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Skipping '{img_path.name}' -> Could not read file")
            continue

        orig_bytes = img_path.stat().st_size
        total_orig_size += orig_bytes

        new_filepath = img_path.with_suffix(".webp")

        encode_params = [
            cv2.IMWRITE_WEBP_QUALITY, 101,
        ]

        success = cv2.imwrite(str(new_filepath), img, encode_params)
        if not success:
            print(f"Failed to encode '{new_filepath.name}'")
            continue

        verified_img = cv2.imread(str(new_filepath))
        if verified_img is None or not np.array_equal(img, verified_img):
            new_filepath.unlink(missing_ok=True)
            print(f"Error: Lossless verification failed for '{img_path.name}'! Original kept.")
            continue

        webp_bytes = new_filepath.stat().st_size
        total_webp_size += webp_bytes

        img_path.unlink()

        saved_pct = (1 - webp_bytes / orig_bytes) * 100
        print(
            f"Processed: '{img_path.name}' -> '{new_filepath.name}' | "
            f"{orig_bytes / (1024 * 1024):.2f}MB -> {webp_bytes / (1024 * 1024):.2f}MB "
            f"(-{saved_pct:.1f}%)"
        )

    print("-" * 50)
    print(
        f"Total: {total_orig_size / (1024 * 1024):.2f} MB -> "
        f"{total_webp_size / (1024 * 1024):.2f} MB"
    )
    if total_orig_size > 0:
        overall_saved = (1 - total_webp_size / total_orig_size) * 100
        print(f"Overall reduction: -{overall_saved:.1f}%")


if __name__ == "__main__":
    compress_fixtures()