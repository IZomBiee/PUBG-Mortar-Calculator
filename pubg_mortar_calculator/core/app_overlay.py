import multiprocessing
import queue
import tkinter as tk
from dataclasses import dataclass

import pygetwindow


class Clear: ...


class Stop: ...


class DrawBorders: ...


class Show: ...


class Remove: ...


@dataclass
class ChangeApp:
    new_title: str


@dataclass
class CreateText:
    text: str
    x: int | float
    y: int | float
    color: str = "white"
    font_size: int = 16


@dataclass
class CreateRect:
    x0: int | float
    y0: int | float
    x1: int | float
    y1: int | float
    border_size: int = 3
    border_color: str = "purple"


@dataclass
class CreateCircle:
    x0: int | float
    y0: int | float
    radious: int | float
    border_size: int = 3
    border_color: str = "blue"


@dataclass
class CreateLine:
    x0: int | float
    y0: int | float
    x1: int | float
    y1: int | float
    thickness: int | float
    color: str = "green"


class AppOverlay:
    def __init__(self, target_app_title: str, fps: int = 20):
        self.title = target_app_title
        self.target_fps = fps
        self.target_delay_millis = int(1 / self.target_fps * 1000)

        self._command_queue = multiprocessing.Queue()
        self.command_buffer = []

        self.show = True
        self.width = 100
        self.height = 100

        self.cycle = 10
        self.last_window = None

        self.gui_process = multiprocessing.Process(target=self._run_gui, daemon=True)
        self.gui_process.start()

    def _run_gui(self):
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

        self._command_queue.close()

    def _render_loop(self):
        self.cycle += 1
        if self.cycle >= 10:
            self.cycle = 0

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
            self.last_window = window

        while True:
            try:
                command = self._command_queue.get_nowait()
            except queue.Empty:
                break

            if isinstance(command, Stop):
                self.root.destroy()
                return
            elif isinstance(command, Clear):
                self.command_buffer.clear()
            elif isinstance(command, ChangeApp):
                self.title = command.new_title
            elif isinstance(command, Show):
                self.show = True
            elif isinstance(command, Remove):
                self.show = False
            else:
                self.command_buffer.append(command)

        self.canvas.delete("all")
        for command in self.command_buffer:
            if isinstance(command, CreateText):
                x = int(
                    command.x * self.width
                    if isinstance(command.x, float)
                    else command.x
                )
                y = int(
                    command.y * self.height
                    if isinstance(command.y, float)
                    else command.y
                )
                self.canvas.create_text(
                    x,
                    y,
                    anchor="nw",
                    text=command.text,
                    fill=command.color,
                    font=("Arial", command.font_size, "bold"),
                )
            elif isinstance(command, CreateRect):
                x0 = int(
                    command.x0 * self.width
                    if isinstance(command.x0, float)
                    else command.x0
                )
                y0 = int(
                    command.y0 * self.height
                    if isinstance(command.y0, float)
                    else command.y0
                )
                x1 = int(
                    command.x1 * self.width
                    if isinstance(command.x1, float)
                    else command.x1
                )
                y1 = int(
                    command.y1 * self.height
                    if isinstance(command.y1, float)
                    else command.y1
                )
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    outline=command.border_color,
                    width=command.border_size,
                )
            elif isinstance(command, CreateCircle):
                x0 = int(
                    command.x0 * self.width
                    if isinstance(command.x0, float)
                    else command.x0
                )
                y0 = int(
                    command.y0 * self.height
                    if isinstance(command.y0, float)
                    else command.y0
                )
                radius = int(
                    command.radious * self.width
                    if isinstance(command.radious, float)
                    else command.radious
                )
                self.canvas.create_oval(
                    x0 - radius,
                    y0 - radius,
                    x0 + radius,
                    y0 + radius,
                    outline=command.border_color,
                    width=command.border_size,
                )
            elif isinstance(command, CreateLine):
                x0 = int(
                    command.x0 * self.width
                    if isinstance(command.x0, float)
                    else command.x0
                )
                y0 = int(
                    command.y0 * self.height
                    if isinstance(command.y0, float)
                    else command.y0
                )
                x1 = int(
                    command.x1 * self.width
                    if isinstance(command.x1, float)
                    else command.x1
                )
                y1 = int(
                    command.y1 * self.height
                    if isinstance(command.y1, float)
                    else command.y1
                )
                self.canvas.create_line(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=command.color,
                    width=command.thickness,
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

        if self.last_window is None or not self.show:
            self.root.withdraw()
        else:
            self.root.deiconify()

        self.root.after(self.target_delay_millis, self._render_loop)

    def add_command(self, command):
        self._command_queue.put(command)

    def stop(self):
        self._command_queue.put(Stop())
        self.gui_process.join(timeout=1.0)
        if self.gui_process.is_alive():
            self.gui_process.terminate()


def main():
    import time

    overlay = AppOverlay("D", 10)
    time.sleep(1)

    for x in range(0, 100, 5):
        overlay.add_command(Clear())
        overlay.add_command(CreateText(str(x), x, 50))
        overlay.add_command(CreateRect(x - 5, 0, x + 5, 100))
        time.sleep(0.05)

    overlay.stop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
