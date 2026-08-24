from typing import List

from PIL import Image, ImageDraw

from pcbutils.structs import BoardPattern, Pin, Track, Side


class BoardPatternImageBuilder:
    _step: float  # mm
    _board_pattern: BoardPattern
    _pins: List[Pin]
    _tracks: List[Track]
    _dpi: int
    _antialias_factor: int
    _draw_grid: bool
    _view_side: Side

    def __init__(self, step: float, board_pattern: BoardPattern, dpi: int = 300, antialias_factor: int = 4, draw_grid: bool = True, view_side: Side = Side.FRONT):
        if view_side == Side.BOTH:
            raise ValueError("View side must be front or back")

        self._step = step
        self._board_pattern = board_pattern
        self._pins = board_pattern.pins
        self._tracks = board_pattern.tracks
        self._dpi = dpi
        self._antialias_factor = antialias_factor
        self._draw_grid = draw_grid
        self._view_side = view_side

    def _mm_to_pixels(self, mm: float) -> int:
        # 1 inch = 25.4 mm
        return int(mm * self._dpi / 25.4)

    def _mm_to_scaled_pixels(self, mm: float) -> int:
        return int(mm * self._dpi / 25.4 * self._antialias_factor)

    def build(self, side: Side, for_printing: bool = False):
        if side == Side.BOTH:
            raise ValueError("Side must be front or back")

        width_mm = self._board_pattern.x_indent * 2 + self._board_pattern.x_count * self._step
        height_mm = self._board_pattern.y_indent * 2 + self._board_pattern.y_count * self._step

        scaled_width_px = self._mm_to_scaled_pixels(width_mm)
        scaled_height_px = self._mm_to_scaled_pixels(height_mm)

        image = Image.new('RGBA', (scaled_width_px, scaled_height_px), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        draw = self._place_board(self._board_pattern, draw)

        for track in filter(lambda t: t.side == side or t.side == Side.BOTH, self._tracks):
            draw = self._place_track(track, draw)

        for pin in filter(lambda p: p.side == side or p.side == Side.BOTH, self._pins):
            draw = self._place_pin(pin, draw)

        final_width = scaled_width_px // self._antialias_factor
        final_height = scaled_height_px // self._antialias_factor

        image = image.resize((final_width, final_height), Image.Resampling.LANCZOS)

        image = image.convert('RGB')

        if for_printing == (self._view_side == side):
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        return image

    def _place_board(self, board: BoardPattern, draw: ImageDraw.ImageDraw) -> ImageDraw.ImageDraw:
        left = self._mm_to_scaled_pixels(board.x_indent)
        top = self._mm_to_scaled_pixels(board.y_indent)
        right = self._mm_to_scaled_pixels(board.x_indent + board.x_count * self._step)
        bottom = self._mm_to_scaled_pixels(board.y_indent + board.y_count * self._step)

        left_outer = 0
        top_outer = 0
        right_outer = right + self._mm_to_scaled_pixels(board.x_indent)
        bottom_outer = bottom + self._mm_to_scaled_pixels(board.y_indent)

        draw.rectangle([left_outer, top_outer, right_outer, bottom_outer], outline='gray', width=2 * self._antialias_factor)

        if self._draw_grid:
            for x in range(board.x_count + 1):
                x_pos_mm = board.x_indent + x * self._step
                x_pos = self._mm_to_scaled_pixels(x_pos_mm)
                draw.line([(x_pos, top), (x_pos, bottom)], fill='lightgray', width=1 * self._antialias_factor)

            for y in range(board.y_count + 1):
                y_pos_mm = board.y_indent + y * self._step
                y_pos = self._mm_to_scaled_pixels(y_pos_mm)
                draw.line([(left, y_pos), (right, y_pos)], fill='lightgray', width=1 * self._antialias_factor)

        return draw

    def _place_pin(self, pin: Pin, draw: ImageDraw.ImageDraw) -> ImageDraw.ImageDraw:
        center_x_mm = self._board_pattern.x_indent + pin.x * self._step + self._step / 2
        center_y_mm = self._board_pattern.y_indent + pin.y * self._step + self._step / 2

        center_x = self._mm_to_scaled_pixels(center_x_mm)
        center_y = self._mm_to_scaled_pixels(center_y_mm)

        outer_radius_px = self._mm_to_scaled_pixels(pin.outer_radius)
        inner_radius_px = self._mm_to_scaled_pixels(pin.inner_radius)

        outer_bbox = [
            center_x - outer_radius_px,
            center_y - outer_radius_px,
            center_x + outer_radius_px,
            center_y + outer_radius_px
        ]

        inner_bbox = [
            center_x - inner_radius_px,
            center_y - inner_radius_px,
            center_x + inner_radius_px,
            center_y + inner_radius_px
        ]

        draw.ellipse(outer_bbox, fill='black')
        draw.ellipse(inner_bbox, fill='white')

        return draw

    def _place_track(self, track: Track, draw: ImageDraw.ImageDraw) -> ImageDraw.ImageDraw:
        start_x_mm = self._board_pattern.x_indent + track.x * self._step + self._step / 2
        start_y_mm = self._board_pattern.y_indent + track.y * self._step + self._step / 2

        end_x_mm = self._board_pattern.x_indent + (track.x + track.x_count) * self._step + self._step / 2
        end_y_mm = self._board_pattern.y_indent + (track.y + track.y_count) * self._step + self._step / 2

        start_x = self._mm_to_scaled_pixels(start_x_mm)
        start_y = self._mm_to_scaled_pixels(start_y_mm)
        end_x = self._mm_to_scaled_pixels(end_x_mm)
        end_y = self._mm_to_scaled_pixels(end_y_mm)

        width_px = max(self._antialias_factor, self._mm_to_scaled_pixels(track.width))

        draw.line([(start_x, start_y), (end_x, end_y)], fill='black', width=width_px)

        radius_px = max(self._antialias_factor, width_px // 2)

        draw.ellipse([
            start_x - radius_px, start_y - radius_px,
            start_x + radius_px, start_y + radius_px
        ], fill='black')

        draw.ellipse([
            end_x - radius_px, end_y - radius_px,
            end_x + radius_px, end_y + radius_px
        ], fill='black')

        return draw
