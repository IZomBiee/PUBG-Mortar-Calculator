import os
from pathlib import Path
from typing import Any, Tuple

import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from torch.utils.data import Dataset
from torchvision import transforms

from tools.minimap_model import shared


class MinimapDataset(Dataset):
    def __init__(self, dataset_path: Path, train: bool = True, transform=None):
        self.transform = transform

        sub_dir = "train" if train else "val"
        label_dir = dataset_path / "labels" / sub_dir
        image_dir = dataset_path / "images" / sub_dir

        self.image_paths = []
        self.labels = []

        label_files = sorted(os.listdir(label_dir))

        for file_name in label_files:
            label_path = label_dir / file_name
            stem = label_path.stem

            img_path = image_dir / f"{stem}.png"
            if not img_path.exists():
                img_path = image_dir / f"{stem}.jpg"
            if not img_path.exists():
                continue

            with open(label_path, "r") as f:
                line = f.readline().strip()

            if len(line) < 5:
                label = 0
            else:
                parts = line.split()
                w = float(parts[3])
                h = float(parts[4])
                area = w * h
                label = 2 if area > 0.06 else 1

            self.image_paths.append(img_path)
            self.labels.append(label)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> Tuple[Any, int]:
        image = Image.open(self.image_paths[index]).convert("RGB")

        if self.transform is not None:
            image = self.transform(image)

        return image, self.labels[index]


class SquarePad:
    def __call__(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        max_dim = max(w, h)
        pad_left = (max_dim - w) // 2
        pad_top = (max_dim - h) // 2
        pad_right = max_dim - w - pad_left
        pad_bottom = max_dim - h - pad_top

        padding = (pad_left, pad_top, pad_right, pad_bottom)
        return ImageOps.expand(img, padding, fill=0)


if __name__ == "__main__":
    dataset = MinimapDataset(shared.DATASET_PATH, True, transform=transforms.ToTensor())

    classes = ["No Minimap", "Small Minimap", "Large Minimap"]

    fig, axes = plt.subplots(4, 4, figsize=(10, 5))

    axes_flat = axes.flatten()

    index = 0
    for image_tensor, label in dataset:
        image = image_tensor.detach().cpu()
        image = image.permute(1, 2, 0)

        axes_flat[index].imshow(image.clamp(0, 1))
        axes_flat[index].set_title(classes[label])
        axes_flat[index].axis("off")
        index += 1
        if index >= 16:
            break

    plt.tight_layout()
    plt.show()
