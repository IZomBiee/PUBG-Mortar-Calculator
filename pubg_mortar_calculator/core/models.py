from dataclasses import dataclass
from typing import Tuple

from pubg_mortar_calculator.detectors.minimap_detector import MinimapType


@dataclass
class GridSettings:
    canny1: int
    canny2: int
    line_threshold: float
    line_gap: float
    line_merge: int
    show_processed: bool
    draw_lines: bool


@dataclass
class OverlaySettings:
    enabled: bool
    draw_borders: bool
    scale: int
    draw_minimap: bool
    draw_map_marks: bool
    draw_elevation_marks: bool


@dataclass
class MarkSettings:
    use_yolo: bool
    color: str
    min_radius: int
    max_radius: int
    draw_marks: bool
    zoom_to_points: bool
    show_processed: bool


@dataclass
class MinimapSettings:
    enabled: bool
    offset: int
    small_size: int
    large_size: int


@dataclass
class ElevationSettings:
    fov: float
    draw_processed: bool
    draw_points: bool


@dataclass
class DictorSettings:
    enabled: bool
    volume: int
    rate: int


@dataclass
class GeneralSettings:
    debug_mode: bool
    calculation_hotkey: str
    elevation_hotkey: str
    all_in_one_hotkey: str
    app_title: str
    monitor_id: int


@dataclass
class MapData:
    distance: float | None = None
    grid_gap: float | None = None
    player_position: tuple[int, int] | None = None
    mark_position: tuple[int, int] | None = None
    minimap_type: MinimapType = MinimapType.NO_MINIMAP
    minimap_box: None | Tuple[int, int, int, int] = None


@dataclass
class ElevationData:
    elevation: float | None = None
    mark_position: tuple[int, int] | None = None
    center_position: tuple[int, int] | None = None
    elevated_distance: float | None = None
    mortar_elevated_distance: int | str | None = None
    x_start: int = 0
