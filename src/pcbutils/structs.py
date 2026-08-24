from enum import Enum
from typing import List, Optional

class Side(Enum):
    BACK = "back"
    FRONT = "front"
    BOTH = "both"


class Pin:
    side: Side
    x: float
    y: float
    outer_radius: float
    inner_radius: float

    def __init__(self, side: Side, x: float, y: float, outer_radius: float, inner_radius: Optional[float] = None):
        self.side = side
        self.x = x
        self.y = y
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius if inner_radius is not None else 0.0


class Track:
    side: Side
    x: float
    y: float
    x_count: float
    y_count: float
    width: float

    def __init__(self, side: Side, x: float, y: float, x_count: float, y_count: float, width: float):
        self.side = side
        self.x = x
        self.y = y
        self.x_count = x_count
        self.y_count = y_count
        self.width = width


class MultiTrack:
    _side: Side
    _x_start: float
    _y_start: float
    _width: float
    _tracks: List[Track]

    def __init__(self, side: Side, x_start: float, y_start: float, width: float):
        self._side = side
        self._x_start = x_start
        self._y_start = y_start
        self._width = width
        self._tracks = []

    def move(self, x_offset: float, y_offset: float) -> "MultiTrack":
        self._tracks.append(Track(
            side=self._side,
            x=self._x_start,
            y=self._y_start,
            x_count=x_offset,
            y_count=y_offset,
            width=self._width,
        ))

        self._x_start += x_offset
        self._y_start += y_offset

        return self

    @property
    def tracks(self) -> List[Track]:
        return list(self._tracks)


class BoardPattern:
    x_count: int
    y_count: int
    x_indent: float
    y_indent: float

    pins: List[Pin]
    tracks: List[Track]

    def __init__(self, pins: List[Pin], tracks: List[Track], x_count: Optional[int] = None, y_count: Optional[int] = None, x_indent: float = 0, y_indent: float = 0):
        if x_count is None:
            x_count = self._compute_count(
                values=[pin.x for pin in pins],
                offsets=[(track.x, track.x_count) for track in tracks],
            )
        if y_count is None:
            y_count = self._compute_count(
                values=[pin.y for pin in pins],
                offsets=[(track.y, track.y_count) for track in tracks],
            )

        self.x_count = x_count
        self.y_count = y_count
        self.x_indent = x_indent
        self.y_indent = y_indent

        self.pins = pins
        self.tracks = tracks

    @staticmethod
    def _compute_count(values: List[float], offsets: List[tuple]) -> int:
        max_index = -1
        for v in values:
            max_index = max(max_index, int(v))
        for start, count in offsets:
            max_index = max(max_index, int(start), int(start + count))
        return max_index + 1 if max_index >= 0 else 0
