import pytest

from pcbutils.factories import PinFactory, TrackFactory
from pcbutils.structs import MultiTrack, Pin, Side, Track


@pytest.mark.parametrize("outer_override, inner_override, expected_outer, expected_inner", [
    (None, None, 2.0, 1.0),
    (3.0, None, 3.0, 1.0),
    (None, 0.5, 2.0, 0.5),
    (3.0, 0.5, 3.0, 0.5),
])
def test_pin_factory_overrides(outer_override, inner_override, expected_outer, expected_inner):
    factory = PinFactory(outer_radius=2.0, inner_radius=1.0)
    pin = factory.create_pin(
        side=Side.FRONT,
        x=1.0,
        y=2.0,
        outer_radius=outer_override,
        inner_radius=inner_override,
    )

    assert isinstance(pin, Pin)
    assert pin.side == Side.FRONT
    assert pin.x == 1.0
    assert pin.y == 2.0
    assert pin.outer_radius == expected_outer
    assert pin.inner_radius == expected_inner


@pytest.mark.parametrize("width_override, expected_width", [
    (None, 1.5),
    (2.5, 2.5),
])
def test_track_factory_create_track_overrides(width_override, expected_width):
    factory = TrackFactory(width=1.5)
    track = factory.create_track(
        side=Side.BACK,
        x=1.0,
        y=2.0,
        x_count=3.0,
        y_count=4.0,
        width=width_override,
    )

    assert isinstance(track, Track)
    assert track.side == Side.BACK
    assert track.x == 1.0
    assert track.y == 2.0
    assert track.x_count == 3.0
    assert track.y_count == 4.0
    assert track.width == expected_width


@pytest.mark.parametrize("width_override, expected_width", [
    (None, 1.5),
    (2.5, 2.5),
])
def test_track_factory_create_multi_track_overrides(width_override, expected_width):
    factory = TrackFactory(width=1.5)
    mt = factory.create_multi_track(
        side=Side.FRONT,
        x_start=1.0,
        y_start=2.0,
        width=width_override,
    )

    assert isinstance(mt, MultiTrack)
    assert mt.tracks == []
