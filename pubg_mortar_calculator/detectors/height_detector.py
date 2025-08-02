import cv2
import numpy as np
import math

class HeightDetector:
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
        t = (distance - 110) / (700 - 110)
        k = 0.4 + (0.55 - 0.4) * (1.1 * t - 0.1 * t**2)
        
        return distance + elevation * k
    
