import multiprocessing
import tkinter as tk

import pygetwindow

from .commands import *


class AppOverlay:
    def __init__(self, target_app_title: str, fps: int = 10):
        self.title = target_app_title
        self.target_fps = fps
        self.target_delay_millis = int(1 / self.target_fps * 1000)

        self._command_queue = multiprocessing.Queue()

        self.command_buffer = []

        self.show = True

        self.width = 100
        self.height = 100

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
        windows = pygetwindow.getAllWindows()
        window = None
        for win in windows:
            if win is not None and self.title in win.title:
                self.root.geometry(
                    f"{win.width}x{win.height}+{win.topleft[0]}+{win.topleft[1]}"
                )
                self.width = win.width
                self.height = win.height
                window = win

        while not self._command_queue.empty():
            command = self._command_queue.get()

            if isinstance(command, Stop):
                self._command_queue.close()
                exit(0)
            elif isinstance(command, Clear):
                self.command_buffer = []
            elif isinstance(command, ChangeApp):
                self.title = command.new_title
            elif isinstance(command, Show):
                self.show = True
            elif isinstance(command, Remove):
                self.show = False
            self.command_buffer.append(command)

        self.canvas.delete("all")
        for command in self.command_buffer:
            if isinstance(command, CreateText):
                if isinstance(command.x, float):
                    x = command.x * self.width
                else:
                    x = command.x
                if isinstance(command.y, float):
                    y = command.y * self.height
                else:
                    y = command.y

                x = int(x)
                y = int(y)

                self.canvas.create_text(
                    x,
                    y,
                    anchor="nw",
                    text=command.text,
                    fill=command.color,
                    font=("Arial", command.font_size, "bold"),
                )
            elif isinstance(command, CreateRect):
                if isinstance(command.x0, float):
                    x0 = command.x0 * self.width
                else:
                    x0 = command.x0
                if isinstance(command.y0, float):
                    y0 = command.y0 * self.height
                else:
                    y0 = command.y0

                if isinstance(command.x1, float):
                    x1 = command.x1 * self.width
                else:
                    x1 = command.x1

                if isinstance(command.y1, float):
                    y1 = command.y1 * self.height
                else:
                    y1 = command.y1

                x0 = int(x0)
                y0 = int(y0)
                x1 = int(x1)
                y1 = int(y1)

                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    outline=command.border_color,
                    width=command.border_size,
                )
            elif isinstance(command, DrawBorders):
                self.canvas.create_rectangle(
                    0,
                    0,
                    self.width,
                    self.height,
                    width=30,
                    outline="yellow",
                )

        if window is None or not self.show:
            self.root.withdraw()
        else:
            self.root.deiconify()

        self.root.after(self.target_delay_millis, self._render_loop)

    def add_command(self, command):
        self._command_queue.put(command)
