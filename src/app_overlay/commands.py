from dataclasses import dataclass


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
