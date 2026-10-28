from pathlib import Path
from tkinter import filedialog


def project() -> Path:
    return Path(__file__).resolve().parents[2]


def assets() -> Path:
    return project() / "assets"


def mortar_distances() -> Path:
    return assets() / "mortar_distances.txt"


def settings() -> Path:
    return project() / "settings.json"


def temp() -> Path:
    return project() / "temp"


def map_preview() -> Path:
    return temp() / "map_preview.png"


def elevation_preview() -> Path:
    return temp() / "elevation_preview.png"


def debug_files() -> Path:
    path = project() / "debug_files"
    path.mkdir(parents=True, exist_ok=True)
    return path


def map_detection_model() -> Path:
    return assets() / "map_model.onnx"


def mark_detection_model() -> Path:
    return assets() / "mark_model.onnx"


def get_image() -> Path | None:
    image_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=[
            ("Image Files", "*.png;*.jpg;*.webp;*.jpeg"),
            ("PNG Files", "*.png"),
            ("JPG Files", "*.jpg"),
            ("JPEG Files", "*.jpeg"),
            ("WEBP Files", "*.webp"),
        ],
    )
    return Path(image_path) if image_path else None
