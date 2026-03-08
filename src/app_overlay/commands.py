from dataclasses import dataclass

class Clear:
    ...

class Stop:
    ...

@dataclass
class CreateText:
    text:str 
    x: int
    y: int
    color: str = "white"
    font_size: int = 16

@dataclass
class CreateRect:
    x0: int
    y0: int
    x1: int
    y1: int
    border_size: int = 3
    color: str = "purple"
