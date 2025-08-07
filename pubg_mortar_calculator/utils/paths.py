import os

from tkinter import filedialog

def project() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def assets() -> str:
    path = os.path.join(project(), 'assets')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def settings() -> str:
    return os.path.join(assets(), 'settings.json')

def map_preview() -> str:
    return os.path.join(assets(), 'map_preview.png')

def elevation_preview() -> str:
    return os.path.join(assets(), 'elevation_preview.png')

def test_samples() -> str:
    path = os.path.join(project(), 'test_samples')
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def map_detection_model() -> str:
    return os.path.join(assets(), 'map_model.onnx')

def get_image() -> str:
    image_path: str = filedialog.askopenfilename(title="Select a File",
                                                        filetypes=[("Image Files", "*.png;*.jpg"),
                                                                   ("PNG Files", "*.png"),
                                                                   ("JPG Files", "*.jpg")])
    return image_path
