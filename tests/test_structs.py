import pytest

from pcbutils.structs import MultiTrack, Pin, Side, Track


@pytest.mark.parametrize("inner_radius, expected", [
    (2.0, 2.0),
    (None, 0.0),
])
def test_pin_inner_radius_default(inner_radius, expected):
    pin = Pin(side=Side.FRONT, x=0.0, y=0.0, outer_radius=3.0, inner_radius=inner_radius)
    assert pin.inner_radius == expected


@pytest.mark.parametrize("x_offset, y_offset", [
    (1.0, 2.0),
    (-1.5, 0.5),
    (0.0, 0.0),
])
def test_multi_track_move_creates_track(x_offset, y_offset):
    mt = MultiTrack(side=Side.FRONT, x_start=0.0, y_start=0.0, width=1.0)
    result = mt.move(x_offset, y_offset)

    assert result is mt
    assert len(mt.tracks) == 1

    track = mt.tracks[0]
    assert isinstance(track, Track)
    assert track.x == 0.0
    assert track.y == 0.0
    assert track.x_count == x_offset
    assert track.y_count == y_offset
    assert track.width == 1.0
    assert track.side == Side.FRONT


@pytest.mark.parametrize("moves, expected_starts", [
    ([(1.0, 0.0), (0.0, 1.0)], [(0.0, 0.0), (1.0, 0.0)]),
    ([(2.0, 3.0), (-1.0, 1.0)], [(0.0, 0.0), (2.0, 3.0)]),
    ([(1.0, 1.0), (1.0, 1.0), (1.0, 1.0)], [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]),
])
def test_multi_track_chained_moves_shift_start(moves, expected_starts):
    mt = MultiTrack(side=Side.BOTH, x_start=0.0, y_start=0.0, width=0.5)
    for offset in moves:
        mt.move(*offset)

    assert len(mt.tracks) == len(moves)
    for track, (x, y) in zip(mt.tracks, expected_starts):
        assert track.x == x
        assert track.y == y


def test_multi_track_tracks_returns_copy():
    mt = MultiTrack(side=Side.FRONT, x_start=0.0, y_start=0.0, width=1.0)
    mt.move(1.0, 0.0)

    tracks_first = mt.tracks
    tracks_first.append(Track(Side.FRONT, 0, 0, 0, 0, 0))
    tracks_second = mt.tracks

    assert len(tracks_second) == 1
