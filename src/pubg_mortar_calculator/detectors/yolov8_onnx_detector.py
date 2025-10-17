import numpy as np
import cv2

from yolov8_onnx import DetectEngine

class YOLOv8OnnxDetector:
    def __init__(self, model_path:str, input_size: int, classes:list[str],
                 conf_thres = 0.2, iou_thres = 0.2) -> None:
        self.classes = classes
        self.input_size = input_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres

        self.engine = DetectEngine(
            model_path,
            self.input_size,
            self.conf_thres,
            self.iou_thres
        )

    def letterbox(self, image: np.ndarray,
                  size: tuple[int, int], fill_value: int = 114):
        original_shape = image.shape[:2]
        r = min(size[0] / original_shape[0], size[1] / original_shape[1])
        new_unpadded = (int(round(original_shape[1] * r)), int(round(original_shape[0] * r)))

        resized = cv2.resize(image, new_unpadded, interpolation=cv2.INTER_LINEAR)
        dw = size[1] - new_unpadded[0]
        dh = size[0] - new_unpadded[1]
        dw /= 2
        dh /= 2

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        padded = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                    cv2.BORDER_CONSTANT, value=(fill_value,) * 3)

        return padded, r, (dw, dh)

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        self.original_shape = image.shape[:2]
        image, self.scale, self.pad = self.letterbox(image, (self.input_size, self.input_size))
        return image

    def postprocess(self, output) -> list[dict]:
        height, width = self.original_shape
        scale = self.scale
        pad_w, pad_h = self.pad
        results = []
        
        for i in range(0, len(output), 3):
            x0, y0, x1, y1 = output[i][0]
            conf = float(output[i + 1][0])
            cls = int(output[i + 2][0])

            x0 = max((x0 - pad_w) / scale, 0)
            y0 = max((y0 - pad_h) / scale, 0)
            x1 = min((x1 - pad_w) / scale, width)
            y1 = min((y1 - pad_h) / scale, height)

            results.append({
                'box':(int(x0), int(y0), int(x1), int(y1)),
                'conf': conf,
                'class': self.classes[cls]
                })
        self.last_results = results
        return results

    def detect(self, image: np.ndarray) -> list[dict]:
        preprocessed = self.preprocess(image)
        output = self.engine(preprocessed)
        if len(output[0]) < 1:
            return []
        return self.postprocess(output)

    def draw(self, image: np.ndarray, results: list[dict]) -> np.ndarray:
        for result in results:
            x0, y0, x1, y1 = result['box']
            conf, cls_id = result['conf'], result['class']
            label = f"{cls_id}: {conf:.2f}"

            cv2.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2.putText(image, label, (x0, y0 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        return image