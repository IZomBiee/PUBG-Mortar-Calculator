import numpy as np
import mouse
import cv2
import os 
from PIL import Image as IMG
from customtkinter import CTkFrame, CTkLabel, CTkImage

class Image:
    def __init__(self, master:CTkFrame, size:tuple[int, int],
                 image_array_or_path:np.ndarray | str | None=None,
                 save_aspect_ratio: bool=False):
        self.label = CTkLabel(master, text='')
        self.size=size
        self.save_aspect_ratio = save_aspect_ratio
        if image_array_or_path is None:
            self.set_cv2(np.zeros((size[1], size[0], 3), dtype=np.uint8))
        elif isinstance(image_array_or_path, str):
            self.set_path(image_array_or_path)
        else:
            self.set_cv2(image_array_or_path)

    def grid(self, row=0, column=0, **kwargs) -> "Image":
        self.label.grid(row=row, column=column, **kwargs)
        return self
    
    def set_path(self, path:str) -> np.ndarray | None:
        if os.path.exists(path):
            image = cv2.imread(path)
            self.set_cv2(image)
            return image
        return None

    def set_cv2(self, array: np.ndarray) -> np.ndarray:
        self.image = array

        if self.save_aspect_ratio:
            self.resized_image = self.resize_with_aspect_ratio(self.image, self.size)
        else:
            self.resized_image = cv2.resize(self.image, self.size, interpolation=cv2.INTER_AREA)

        pillow_image = self._cv2_to_pillow(self.resized_image)
        self.label.configure(image=CTkImage(pillow_image, pillow_image, self.size))
        return self.image
        
    def _cv2_to_pillow(self, frame, cv2_color_key:int=cv2.COLOR_BGR2RGB) -> IMG.Image:
        if cv2_color_key != None:
            frame = cv2.cvtColor(frame, cv2_color_key)
        return IMG.fromarray(frame)

    def get_current(self) -> np.ndarray:
        return self.image
    
    def get_mouse_pos(self, real_position=False) -> None | list[int]:
        mouse_x, mouse_y = mouse.get_position()

        widget_x = self.label.winfo_rootx()
        widget_y = self.label.winfo_rooty()
        widget_width = self.label.winfo_width()
        widget_height = self.label.winfo_height()

        relative_x = mouse_x - widget_x
        relative_y = mouse_y - widget_y

        if relative_x > widget_width or relative_y > widget_height:
            return None
        elif relative_x < 0 or relative_y < 0:
            return None
        else:
            if not real_position:
                image_width = self.image.shape[1]
                image_height = self.image.shape[0]

                scale_x = image_width / widget_width
                scale_y = image_height / widget_height

                scaled_x = int(relative_x * scale_x)
                scaled_y = int(relative_y * scale_y)
                return [scaled_x, scaled_y]
            else:
                return [relative_x, relative_y]

    @staticmethod
    def resize_with_aspect_ratio(image: np.ndarray, output_size: tuple[int, int]) -> np.ndarray:
        original_height, original_width = image.shape[:2]
        target_width, target_height = output_size

        original_aspect = original_width / original_height
        target_aspect = target_width / target_height
        if original_aspect > target_aspect:
            new_width = target_width
            new_height = int(target_width / original_aspect)
        else:
            new_height = target_height
            new_width = int(target_height * original_aspect)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        result[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image
        return result