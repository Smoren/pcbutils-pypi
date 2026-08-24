from typing import Optional

from pcbutils.structs import Pin, Side, Track, MultiTrack


class PinFactory:
    _outer_radius: float
    _inner_radius: Optional[float]

    def __init__(self, outer_radius: float, inner_radius: Optional[float] = None):
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius

    def create_pin(self, side: Side, x: float, y: float, outer_radius: Optional[float] = None, inner_radius: Optional[float] = None) -> Pin:
        outer_radius = outer_radius if outer_radius is not None else self._outer_radius
        inner_radius = inner_radius if inner_radius is not None else self._inner_radius
        return Pin(side=side, x=x, y=y, outer_radius=outer_radius, inner_radius=inner_radius)


class TrackFactory:
    _width: float

    def __init__(self, width: float):
        self._width = width

    def create_track(self, side: Side, x: float, y: float, x_count: float, y_count: float, width: Optional[float] = None) -> Track:
        width = width if width is not None else self._width
        return Track(side=side, x=x, y=y, x_count=x_count, y_count=y_count, width=width)

    def create_multi_track(self, side: Side, x_start: float, y_start: float, width: Optional[float] = None) -> MultiTrack:
        width = width if width is not None else self._width
        return MultiTrack(side=side, x_start=x_start, y_start=y_start, width=width)
