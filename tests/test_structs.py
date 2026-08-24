import pytest

from pcbutils.structs import BoardPattern, MultiTrack, Pin, Side, Track


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


# --- BoardPattern auto-compute x_count/y_count ---

def test_board_pattern_empty_defaults_to_zero():
    pattern = BoardPattern(pins=[], tracks=[])
    assert pattern.x_count == 0
    assert pattern.y_count == 0


@pytest.mark.parametrize("pins, tracks, expected_x, expected_y", [
    # Single pin at origin
    ([Pin(Side.BOTH, 0, 0, 1)], [], 1, 1),
    # Pin at (3, 2)
    ([Pin(Side.BOTH, 3, 2, 1)], [], 4, 3),
    # Two pins — max wins
    ([Pin(Side.BOTH, 1, 5, 1), Pin(Side.BOTH, 4, 1, 1)], [], 5, 6),
    # Track only: x=1, x_count=3 → spans to 4 → count=5
    ([], [Track(Side.BOTH, 1, 0, 3, 0, 0.5)], 5, 1),
    # Track + pin — combined max
    ([Pin(Side.BOTH, 2, 2, 1)], [Track(Side.BOTH, 0, 1, 5, 0, 0.5)], 6, 3),
    # Negative track offset (x_count negative) — pin still defines bounds
    ([Pin(Side.BOTH, 0, 0, 1)], [Track(Side.BOTH, 3, 0, -1, 0, 0.5)], 4, 1),
])
def test_board_pattern_auto_compute(pins, tracks, expected_x, expected_y):
    pattern = BoardPattern(pins=pins, tracks=tracks)
    assert pattern.x_count == expected_x
    assert pattern.y_count == expected_y


@pytest.mark.parametrize("x_count, y_count", [
    (10, 5),
    (1, 1),
])
def test_board_pattern_explicit_overrides_auto(x_count, y_count):
    pin = Pin(Side.BOTH, 3, 3, 1)
    pattern = BoardPattern(pins=[pin], tracks=[], x_count=x_count, y_count=y_count)
    assert pattern.x_count == x_count
    assert pattern.y_count == y_count
