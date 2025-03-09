import os
import json
import time
from customtkinter import *
from pubg_mortar_calculator.custom_widgets import *
from tkinter import messagebox

class AnnotationTool(CTk):
    def __init__(self):
        super().__init__()
        self.preview_image = CustomImage(self, (1000, 1000))
        self.preview_image.grid(row=1, column=1, columnspan=2)

        self.current_sample_label = CTkLabel(self, text='0/0')
        self.current_sample_label.grid(row=0, column=1, columnspan=2)

        self.grid_x_slider = CustomSlider(self, 'Grid X', 0, 400, 200, 400)
        self.grid_y_slider = CustomSlider(self, 'Grid Y', 0, 400, 200, 400)
        self.grid_x_slider.grid(row=3, column=0)
        self.grid_y_slider.grid(row=4, column=0)

        self.left_button = CTkButton(self, height=500, text='<', command=self.left)
        self.left_button.grid(row=1, column=0)

        self.right_button = CTkButton(self, height=500, text='>', command=self.right)
        self.right_button.grid(row=1, column=3)

        self.mark_change_button = CTkButton(self, text='Change Mark Position', command=self.change_mark_position)
        self.mark_change_button.grid(row=2, column=3)
        
        self.player_change_button = CTkButton(self, text='Change Player Position', command=self.change_player_position)
        self.player_change_button.grid(row=3, column=3)
        self.on_startup()
    
    def left(self):
        if self.current_sample-1 < 0: 
            self.set_sample(len(self.samples)-1)
        else:
            self.set_sample(self.current_sample-1)
    
    def right(self):
        if self.current_sample +1 >= len(self.samples):
            self.set_sample(0)
        else:
            self.set_sample(self.current_sample+1)

    def change_player_position(self):
        time.sleep(0.3)
        mouse.wait()
        pos = self.preview_image.get_mouse_pos()
        if pos == None:
            messagebox.showwarning('Warning!', 'You mouse should be on image!')
        self.samples[self.current_sample]['player_cord'] = pos
        self.preview_current_sample()
    
    def change_mark_position(self):
        time.sleep(0.3)
        mouse.wait()
        pos = self.preview_image.get_mouse_pos()
        if pos == None:
            messagebox.showwarning('Warning!', 'You mouse should be on image!')
        self.samples[self.current_sample]['mark_cord'] = pos
        self.preview_current_sample()

    def on_startup(self):
        self.current_sample = 0
        self.load_samples()
        self.set_sample(0)

    def load_samples(self):
        self.samples = filter(lambda x:x.endswith('.json'),os.listdir(f'tests/test_samples/'))
        self.samples = list(map(
            lambda x:  json.load(open(f'tests/test_samples/{x}', 'r')), self.samples
        ))
    
    def preview_current_sample(self):
        image = cv2.imread(f'tests/test_samples/{self.samples[self.current_sample]['image_name']}')
        try:
            self.draw_grid_on_image(image, self.samples[self.current_sample]['grid_gap'])
            cv2.circle(image, self.samples[self.current_sample]['mark_cord'], 30, (255, 0, 0), 5)
            cv2.circle(image, self.samples[self.current_sample]['player_cord'], 30, (0, 0, 255), 5)
        except TypeError:pass
        self.preview_image.set_cv2(image)

    def draw_grid_on_image(self, image, grid_gap):
        height, width = image.shape[:2]

        grid_x = grid_gap[0]
        grid_y = grid_gap[1]

        for x in range(grid_x, width, grid_x):
            cv2.line(image, (x, 0), (x, height), (0, 255, 0), 1)

        for y in range(grid_y, height, grid_y):
            cv2.line(image, (0, y), (width, y), (0, 255, 255), 1)

        return image

    def save_current_sample(self):
        with open(f'tests/test_samples/{'.'.join(self.samples[self.current_sample]['image_name'].split('.')[0:-1])}.json',
                  'w') as file:
            json.dump(self.samples[self.current_sample], file)

    def set_sample(self, index:int):
        self.save_current_sample()
        self.current_sample = index
        self.preview_current_sample()
        try:
            self.grid_x_slider.set(self.samples[index]['grid_gap'][0])
            self.grid_y_slider.set(self.samples[index]['grid_gap'][1])
        except TypeError:pass
        self.current_sample_label.configure(text=f'{self.current_sample+1}/{len(self.samples)}')
        
        
        
app = AnnotationTool()
app.mainloop()