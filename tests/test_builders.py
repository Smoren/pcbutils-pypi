import pytest

from pcbutils.builders import BoardPatternImageBuilder
from pcbutils.structs import BoardPattern, Pin, Side, Track


def _make_pattern(pins=None, tracks=None, x_count=2, y_count=1,
                  x_indent=10.0, y_indent=10.0):
    return BoardPattern(
        x_count=x_count,
        y_count=y_count,
        x_indent=x_indent,
        y_indent=y_indent,
        pins=pins or [],
        tracks=tracks or [],
    )


def _black_pixels_center_x(image):
    """Average X coordinate of black pixels (pins/tracks)."""
    pixels = image.load()
    width, height = image.size
    total = 0
    sum_x = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r < 100 and g < 100 and b < 100:
                total += 1
                sum_x += x
    return sum_x / total if total else -1.0


def _has_black_pixels(image):
    return _black_pixels_center_x(image) >= 0


# --- Pixel conversion ---

@pytest.mark.parametrize("mm, dpi, expected", [
    (25.4, 300, 300),
    (25.4, 150, 150),
    (0.0, 300, 0),
    (1.0, 300, 11),
])
def test_mm_to_pixels(mm, dpi, expected):
    builder = BoardPatternImageBuilder(
        step=10.0, board_pattern=_make_pattern(), dpi=dpi
    )
    assert builder._mm_to_pixels(mm) == expected


# --- Constructor ---

@pytest.mark.parametrize("view_side", [Side.FRONT, Side.BACK])
def test_constructor_accepts_valid_view_side(view_side):
    builder = BoardPatternImageBuilder(
        step=10.0, board_pattern=_make_pattern(), view_side=view_side
    )
    assert builder._view_side == view_side


def test_constructor_rejects_both_view_side():
    with pytest.raises(ValueError):
        BoardPatternImageBuilder(
            step=10.0, board_pattern=_make_pattern(), view_side=Side.BOTH
        )


def test_build_rejects_both_side():
    builder = BoardPatternImageBuilder(step=10.0, board_pattern=_make_pattern())
    with pytest.raises(ValueError):
        builder.build(Side.BOTH)


# --- Mirroring ---

@pytest.mark.parametrize(
    "view_side, side, for_printing, pin_stays_left",
    [
        # view_side, rendered side, for_printing, pin stays on the left?
        (Side.FRONT, Side.FRONT, False, True),   # preview same side: no mirror
        (Side.FRONT, Side.FRONT, True, False),   # print same side: mirror
        (Side.FRONT, Side.BACK, False, False),   # preview opposite: mirror
        (Side.FRONT, Side.BACK, True, True),     # print opposite: no mirror
        (Side.BACK, Side.BACK, False, True),
        (Side.BACK, Side.BACK, True, False),
        (Side.BACK, Side.FRONT, False, False),
        (Side.BACK, Side.FRONT, True, True),
    ],
)
def test_mirroring(view_side, side, for_printing, pin_stays_left):
    # Asymmetric pattern: single pin in the left cell (x=0) of a 2-wide board.
    pin = Pin(side=Side.BOTH, x=0, y=0, outer_radius=3.0, inner_radius=1.0)
    builder = BoardPatternImageBuilder(
        step=10.0, board_pattern=_make_pattern(pins=[pin]), view_side=view_side
    )
    image = builder.build(side, for_printing=for_printing)

    center_x = _black_pixels_center_x(image)
    assert center_x >= 0, "Expected black pixels from the pin"

    if pin_stays_left:
        assert center_x < image.size[0] / 2
    else:
        assert center_x > image.size[0] / 2


# --- Side filtering ---

@pytest.mark.parametrize(
    "pin_side, build_side, visible",
    [
        (Side.FRONT, Side.FRONT, True),
        (Side.FRONT, Side.BACK, False),
        (Side.BACK, Side.BACK, True),
        (Side.BACK, Side.FRONT, False),
        (Side.BOTH, Side.FRONT, True),
        (Side.BOTH, Side.BACK, True),
    ],
)
def test_pin_side_filtering(pin_side, build_side, visible):
    pin = Pin(side=pin_side, x=0, y=0, outer_radius=3.0, inner_radius=1.0)
    builder = BoardPatternImageBuilder(
        step=10.0, board_pattern=_make_pattern(pins=[pin]), draw_grid=False
    )
    image = builder.build(build_side)
    assert _has_black_pixels(image) == visible


@pytest.mark.parametrize(
    "track_side, build_side, visible",
    [
        (Side.FRONT, Side.FRONT, True),
        (Side.FRONT, Side.BACK, False),
        (Side.BACK, Side.BACK, True),
        (Side.BACK, Side.FRONT, False),
        (Side.BOTH, Side.FRONT, True),
        (Side.BOTH, Side.BACK, True),
    ],
)
def test_track_side_filtering(track_side, build_side, visible):
    track = Track(side=track_side, x=0, y=0, x_count=1, y_count=0, width=1.0)
    builder = BoardPatternImageBuilder(
        step=10.0, board_pattern=_make_pattern(tracks=[track]), draw_grid=False
    )
    image = builder.build(build_side)
    assert _has_black_pixels(image) == visible


# --- Image size ---

@pytest.mark.parametrize(
    "x_count, y_count, x_indent, y_indent, dpi, antialias_factor",
    [
        (2, 1, 10.0, 10.0, 300, 4),
        (3, 3, 5.0, 7.5, 150, 2),
        (1, 1, 0.0, 0.0, 600, 1),
        (2, 2, 2.5, 2.5, 300, 1),
    ],
)
def test_image_size(x_count, y_count, x_indent, y_indent, dpi, antialias_factor):
    step = 10.0
    pattern = BoardPattern([], [], x_count, y_count, x_indent, y_indent)
    builder = BoardPatternImageBuilder(
        step=step,
        board_pattern=pattern,
        dpi=dpi,
        antialias_factor=antialias_factor,
        draw_grid=False,
    )
    image = builder.build(Side.FRONT)

    width_mm = x_indent * 2 + x_count * step
    height_mm = y_indent * 2 + y_count * step
    expected_w = int(width_mm * dpi / 25.4 * antialias_factor) // antialias_factor
    expected_h = int(height_mm * dpi / 25.4 * antialias_factor) // antialias_factor

    assert image.size == (expected_w, expected_h)
    assert image.mode == "RGB"
