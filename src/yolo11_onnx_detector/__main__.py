import argparse
import cv2
from . import Yolo11OnnxDetector

def resize_image(image, max_size):
    h, w = image.shape[:2]
    if max(h, w) <= max_size:
        return image
    scale = max_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h))

def main():
    parser = argparse.ArgumentParser(
        description="Run YOLO detection on an image"
    )
    parser.add_argument(
        "-m", "--model", type=str, required=True,
        help="Path to the ONNX model"
    )
    parser.add_argument(
        "-i", "--image", type=str, required=True,
        help="Path to the image file"
    )
    parser.add_argument(
        "-w", "--window", type=str, default="Detection",
        help="Name of the OpenCV window"
    )
    parser.add_argument(
        "--max-size", type=int, default=1000,
        help="Maximum width or height of the displayed image"
    )
    args = parser.parse_args()

    # Load detector
    detector = Yolo11OnnxDetector(args.model, confidence=0.7)

    # Read image
    image = cv2.imread(args.image)
    if image is None:
        print(f"Error: Could not read image {args.image}")
        return

    # Detect and draw
    detector.detect(image)
    detector.draw_last_detections(image)

    # Resize image for display
    image = resize_image(image, args.max_size)

    # Show result
    cv2.imshow(args.window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
