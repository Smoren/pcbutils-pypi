from typing import Optional

from pcbutils.structs import Pin, Side


class PinFactory:
    _outer_radius: float
    _inner_radius: Optional[float]

    def __init__(self, outer_radius: float, inner_radius: Optional[float] = None):
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius

    def create_pin(self, side: Side, x: float, y: float) -> Pin:
        return Pin(side=side, x=x, y=y, outer_radius=self._outer_radius, inner_radius=self._inner_radius)


class TrackFactory:
    _width: float

    def __init__(self, width: float):
        self._width = width
