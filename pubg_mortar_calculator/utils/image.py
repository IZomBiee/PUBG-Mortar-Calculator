import cv2
import numpy as np

def cut_x_line(image:np.ndarray, x:int, gap:float=0.1):
    h, w = image.shape[:2]
    gap = round(w*gap)
    x_start = x - gap
    x_end = x_start + gap*2

    center_strip = image[:, x_start:x_end]
    return center_strip

def replace_area_with_black(image: np.ndarray,
                            point1: tuple[int, int],
                            point2: tuple[int, int]):
    x1, y1 = point1
    x2, y2 = point2

    h, w = image.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    
    if len(image.shape) == 3:
        image[int(y1):int(y2), int(x1):int(x2)] = (0, 0, 0)
    else:
        image[int(y1):int(y2), int(x1):int(x2)] = 0
    
    return image

def draw_point(frame: np.ndarray,
                position: tuple[int, int],
                title: str,
                color: tuple = (255, 0, 0), radius: int = 25,
                thickness:int = 12, font_scale:int=2): 
    cv2.circle(frame, position, radius, color, thickness)

    font_thickness = max(1, int(font_scale * 3))

    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale, font_thickness)[0]
    text_w, text_h = text_size

    bg_x, bg_y = position[0] - text_w // 2, position[1] - text_h - 10
    bg_x = max(0, min(bg_x, frame.shape[1] - text_w))
    bg_y = max(text_h + 10, min(bg_y, frame.shape[0] - 10))

    cv2.rectangle(frame, (bg_x - 5, bg_y - text_h - 5),
                    (bg_x + text_w + 5, bg_y + 5), (0, 0, 0), -1)
    cv2.putText(frame, title, (bg_x, bg_y), cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (255, 255, 255), font_thickness)

def get_center_point(image: np.ndarray) -> tuple[int, int]:
    center_x = image.shape[1]//2
    center_y = image.shape[0]//2
    return (center_x, center_y)

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