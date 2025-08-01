import cv2
import numpy as np
import math
import onnxruntime as ort
import json

from .custom_widgets import CustomImage
from .grid_detector import GridDetector

class HeightDetector:
    def __init__(self):
        self.onnx_session = ort.InferenceSession("models\\corrector_model.onnx")
    
    def get_corrected_distance(self, image: np.ndarray, player_pos: tuple[int, int],
                            mark_pos: tuple[int, int], distance: float) -> float:
        height, width = image.shape[:2]
        
        image = CustomImage.resize_with_aspect_ratio(image, (512, 512))
        
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        normalized_gray_image = gray_image.astype(np.float32) / 255.0
        
        flatten_gray_image = np.expand_dims(np.expand_dims(normalized_gray_image, axis=0), axis=0)

        norm_player_pos = np.array([[player_pos[0]/width, player_pos[1]/height]], dtype=np.float32)
        norm_mark_pos = np.array([[mark_pos[0]/width, mark_pos[1]/height]], dtype=np.float32)

        inputs = {
            "image": flatten_gray_image,
            "norm_player_pos": norm_player_pos.reshape(1, 2),
            "norm_mark_pos": norm_mark_pos.reshape(1, 2),
            "distance_km": np.array([[distance/1000]], dtype=np.float32)
        }
        
        outputs = self.onnx_session.run(None, inputs)
        predicted_km = outputs[0][0][0]
        
        predicted_meters = predicted_km * 1000
        
        return predicted_meters 

    @staticmethod
    def cut_to_points(image: np.ndarray, point1: tuple[int, int],
                    point2: tuple[int, int], margin: float = 0.05) -> np.ndarray:
        height, width = image.shape[:2]
        
        left = min(point1[0], point2[0])
        right = max(point1[0], point2[0])
        top = min(point1[1], point2[1])
        bottom = max(point1[1], point2[1])
        
        margin_x = int(round(width * margin))
        margin_y = int(round(height * margin))
        
        left = max(0, left - margin_x)
        right = min(width, right + margin_x)
        top = max(0, top - margin_y)
        bottom = min(height, bottom + margin_y)
        
        return image[top:bottom, left:right]
            
    @staticmethod
    def draw_point_position(image:np.ndarray,
                            point: tuple[int, int],
                            color: tuple[int, int, int]=(255, 0, 0)) -> np.ndarray:
        x, y = point
        cv2.line(image, (0, y),
                 (image.shape[1], y), color, 3)

        cv2.line(image, (x, 0),
                 (x, image.shape[0]), color, 3)
        return image

    @staticmethod
    def get_center_point(image: np.ndarray) -> tuple[int, int]:
        center_x = image.shape[1]//2
        center_y = image.shape[0]//2
        return (center_x, center_y)
    
    @staticmethod
    def get_elevation(y0: int, y1: int, fov_deg: float, dist: float,
                    aspect_ratio: float = 16/9) -> float:
        vfov_rad = math.atan(math.tan(math.radians(fov_deg) / 2) / aspect_ratio) * 2

        pixels_from_center = y1-y0

        angle_rad = math.atan(math.tan(vfov_rad / 2) / y0 * pixels_from_center)

        elevation = math.tan(angle_rad) * dist

        return -elevation
    
    @staticmethod
    def get_correct_distance(elevation:float, distance:float) -> float:
        return distance+(elevation*0.76)

    @staticmethod
    def cut_x_line(image:np.ndarray, x:int, gap:int=100):
        h, w = image.shape[:2]
        x_start = x - gap
        x_end = x_start + gap*2

        center_strip = image[:, x_start:x_end]
        return center_strip

if __name__ == '__main__':
    detector = HeightDetector()
    name = '2025-07-28_11-55-26'
    image = cv2.imread(rf'tests\test_samples\{name}.png')
    with open(rf'tests\test_samples\{name}.json', 'r') as file:
        data = json.load(file)
    distance = GridDetector.get_distance(data['player_position'],
                    data['mark_position'],
                    data['grid_gap'])
    elevation = HeightDetector.get_elevation(
        HeightDetector.get_center_point(image)[1],
        round(HeightDetector.get_center_point(image)[1]*1.10), 90, distance)
    predicted_distance = HeightDetector.get_correct_distance(elevation, distance)
    print(f"Line-Off-Sight Distance: {distance}")
    print(f"Real Distance: {data['real_distance']}")
    print(f"Elevation: {elevation}")
    print(f"Predicted Distance: {predicted_distance}")