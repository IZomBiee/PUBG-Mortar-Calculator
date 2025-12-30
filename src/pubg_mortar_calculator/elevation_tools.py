import cv2
import numpy as np
import math

class ElevationTools:
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
    
    # Inspirated by: https://github.com/Ashimdude/mortarkiller_desktop
    @staticmethod
    def get_elevation(y0: int, y1: int, fov_deg: float, dist: float,
                    aspect_ratio: float = 16/9) -> float:
        vfov_rad = math.atan(math.tan(math.radians(fov_deg) / 2) / aspect_ratio) * 2

        pixels_from_center = y1-y0

        angle_rad = math.atan(math.tan(vfov_rad / 2) / y0 * pixels_from_center)

        elevation = math.tan(angle_rad) * dist

        return -elevation
    
    # Borrowed from: https://github.com/Iamnotphage/MortarAid4PUBG/tree/main
    @staticmethod
    def get_elevated_distance(distance: float, elevation: float) -> float:
        max_mortar_distance = 700.0
        if elevation == 0: return distance
        tan_beta = elevation / distance

        discriminant = max_mortar_distance**2 - 2 * distance * max_mortar_distance * tan_beta - distance**2

        if discriminant < 0:
            return 0

        sqrt_term = math.sqrt(discriminant)

        elevated_distance = (distance + tan_beta * (max_mortar_distance - sqrt_term)) / (tan_beta**2 + 1)

        return elevated_distance
    
if __name__ == '__main__':
    elevation = -75
    distance = 217
    elevated_distance = ElevationTools.get_elevated_distance(distance, elevation)
    print(f"Distance: {distance} Elevation: {elevation} Elevated distance: {elevated_distance}")