from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as ort
import torchvision.transforms as transforms
from PIL import Image
import torchvision.transforms.functional as F

from tools.minimap_model import shared

def test_single_image(image_path: Path):
    onnx_path = Path("tools/minimap_model/best_int8.onnx")
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    image_pil = Image.open(image_path).convert("RGB")
    image_tensor = shared.VAL_TRANSFORM(image_pil)
    input_numpy = image_tensor.unsqueeze(0).numpy()

    outputs = session.run([output_name], {input_name: input_numpy})
    logits = outputs[0][0]

    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / np.sum(exp_logits)

    img_np = image_tensor.permute(1, 2, 0).numpy()
    img_display = np.clip(img_np * shared.STD + shared.MEAN, 0, 1)

    plt.figure(figsize=(5, 5))
    plt.imshow(img_display)
    plt.title(
        f"Pred: {[round(float(i), 2) for i in probs]}",
        fontsize=12,
        fontweight="bold",
        color="green",
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_image_path = Path(
        r"tests\fixtures\TslGame_bDodaZ2l4Y.webp"
    )
    test_single_image(test_image_path)
