import cv2
import numpy as np

import cv2
import numpy as np

def get_straight_line(image: np.ndarray,
                      start_point: tuple[int, int],
                      end_point: tuple[int, int],
                      width: float = 0.1,
                      margin: float = 0.0) -> np.ndarray:
    x1, y1 = start_point
    x2, y2 = end_point
    H, W = image.shape[:2]

    abs_width = width * min(H, W)

    dx = x2 - x1
    dy = y2 - y1
    length = np.hypot(dx, dy)

    if length == 0:
        raise ValueError("Start and end points cannot be the same.")

    # Unit direction vector
    dir_x = dx / length
    dir_y = dy / length

    # Add margin (in both directions)
    margin_len = length * margin
    x1m = x1 - dir_x * margin_len
    y1m = y1 - dir_y * margin_len
    x2m = x2 + dir_x * margin_len
    y2m = y2 + dir_y * margin_len

    extended_length = np.hypot(x2m - x1m, y2m - y1m)

    # Perpendicular unit vector
    perp_dx = -dir_y
    perp_dy = dir_x

    # Rectangle corners with margin
    p1 = (x1m + perp_dx * abs_width / 2, y1m + perp_dy * abs_width / 2)
    p2 = (x2m + perp_dx * abs_width / 2, y2m + perp_dy * abs_width / 2)
    p3 = (x2m - perp_dx * abs_width / 2, y2m - perp_dy * abs_width / 2)
    p4 = (x1m - perp_dx * abs_width / 2, y1m - perp_dy * abs_width / 2)

    src_pts = np.array([p1, p2, p3, p4], dtype=np.float32)
    dst_pts = np.array([
        [0, 0],
        [extended_length, 0],
        [extended_length, abs_width],
        [0, abs_width]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, (int(extended_length), int(abs_width)))

    return warped

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
               color: tuple = (255, 0, 0),
               radius: float = 0.02,
               thickness: float = 0.005,
               font_scale: float = 0.002):
    h, w = frame.shape[:2]
    base = min(h, w)

    radius_px = max(1, int(radius * base))
    thickness_px = max(1, int(thickness * base))
    font_scale_px = font_scale * base

    cv2.circle(frame, position, radius_px, color, thickness_px)

    font_thickness = max(1, int(font_scale_px * 0.5))

    text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale_px, font_thickness)[0]
    text_w, text_h = text_size

    bg_x, bg_y = position[0] - text_w // 2, position[1] - text_h - 10
    bg_x = max(0, min(bg_x, w - text_w))
    bg_y = max(text_h + 10, min(bg_y, h - 10))

    cv2.rectangle(frame, (bg_x - 5, bg_y - text_h - 5),
                  (bg_x + text_w + 5, bg_y + 5), (0, 0, 0), -1)

    cv2.putText(frame, title, (bg_x, bg_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale_px, (255, 255, 255), font_thickness)

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

def letterbox(img: np.ndarray, size: tuple[int, int], fill_value: int = 114) -> np.ndarray:
    target_h, target_w = size
    h, w = img.shape[:2]

    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    padded_img = np.full((target_h, target_w, 3), fill_value, dtype=img.dtype)

    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2

    padded_img[top:top + new_h, left:left + new_w] = resized_img

    return padded_img