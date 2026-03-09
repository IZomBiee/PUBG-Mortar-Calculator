import time

from .app_overlay import AppOverlay
from .commands import *


def main():
    overlay = AppOverlay(".png", 10)

    time.sleep(1)

    x = 0
    while True:
        overlay.add_command(Clear())
        x += 5

        overlay.add_command(CreateText(str(x), x, 50))
        overlay.add_command(CreateRect(x - 5, 0, x + 5, 100))

        time.sleep(0.05)
