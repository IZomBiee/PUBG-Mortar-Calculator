import numpy as np
import torchvision
import torchvision.transforms.functional as F
from torchvision import transforms
from pathlib import Path

DATASET_PATH = Path(r"C:\Users\patri\Desktop\map_dataset")
EPOCH_COUNT = 15
BATCH_SIZE = 16
CUT_FACTOR = 0.35
RESOLUTION = 128*2
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

cut_transform = transforms.Lambda(lambda img: F.crop(
        img,
        top=img.height - round(img.width * CUT_FACTOR),
        left=img.width - round(img.width * CUT_FACTOR),
        height=round(img.width * CUT_FACTOR),
        width=round(img.width * CUT_FACTOR)
        ))

TRAIN_TRANSFORM = torchvision.transforms.Compose(
    [
        cut_transform,
        transforms.Resize((RESOLUTION, RESOLUTION)),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD),
    ]
)

VAL_TRANSFORM = torchvision.transforms.Compose(
    [
        cut_transform,
        transforms.Resize((RESOLUTION, RESOLUTION)),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD),
    ]
)