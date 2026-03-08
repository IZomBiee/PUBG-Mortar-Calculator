import queue
import multiprocessing
import time
import tkinter as tk
import pygetwindow
import ctypes

from .commands import *

class AppOverlay:
    def __init__(self, target_app_title: str, fps: int = 10):
        self.title = target_app_title
        self.target_fps = fps
        self.target_delay_millis = int(1/self.target_fps*1000)
        
        self._command_queue = multiprocessing.Queue()
        
        self.gui_process = multiprocessing.Process(target=self._run_gui, daemon=True)
        self.gui_process.start()

    def _run_gui(self):
        self.elements = []
        
        self.root = tk.Tk()
        self.root.title("PUBG Overlay")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.withdraw()

        self._render_loop()
        
        self.root.mainloop()

    def _render_loop(self):        
        window = pygetwindow.getActiveWindow()
        if window is not None and self.title in window.title:
            self.root.deiconify()
            self.root.geometry(f"{window.width}x{window.height}+{window.topleft[0]}+{window.topleft[1]}")
        else:
            self.root.withdraw()

        while not self._command_queue.empty():
            command = self._command_queue.get()
            if isinstance(command, Stop):
                self._command_queue.close()
                exit(0)
            elif isinstance(command, Clear):
                self.canvas.delete("all")
            elif isinstance(command, CreateText):
                self.canvas.create_text(
                    command.x, command.y, 
                    text=command.text, 
                    fill=command.color, 
                    font=("Arial", command.font_size, "bold")
                )
            elif isinstance(command, CreateRect):
                self.canvas.create_rectangle(command.x0, command.y0, command.x1,
                                             command.y1, outline=command.color, 
                    width=command.border_size)
            
        self.root.after(self.target_delay_millis, self._render_loop)
    
    def add_command(self, command):
        self._command_queue.put(command)
    
