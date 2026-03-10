import os
from tkinter import filedialog


def project() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def assets() -> str:
    return os.path.join(project(), "assets")


def mortar_distances() -> str:
    return os.path.join(assets(), "mortar_distances.txt")


def settings() -> str:
    return os.path.join(project(), "settings.json")


def temp() -> str:
    return os.path.join(project(), "temp")


def map_preview() -> str:
    return os.path.join(temp(), "map_preview.png")


def elevation_preview() -> str:
    return os.path.join(temp(), "elevation_preview.png")


def debug_files() -> str:
    path = os.path.join(project(), "debug_files")
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def map_detection_model() -> str:
    return os.path.join(assets(), "map_model.onnx")


def mark_detection_model() -> str:
    return os.path.join(assets(), "mark_model.onnx")


def get_image() -> str:
    image_path: str = filedialog.askopenfilename(
        title="Select a File",
        filetypes=[
            ("Image Files", "*.png;*.jpg"),
            ("PNG Files", "*.png"),
            ("JPG Files", "*.jpg"),
        ],
    )
    return image_path
