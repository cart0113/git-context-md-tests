from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from od_do.diagram.base import Diagram
from od_do import shapes, colors
from od_do.shapes import text
from od_do.paths import Line
from od_do.geometry import Point
from od_do.colors import ColorLike, Color

if TYPE_CHECKING:
    pass


class Resistor(Diagram):
    def __init__(
        self,
        style: str = "american",
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        body_width: float = 60,
        body_height: float = 20,
        terminal_length: float = 8,
        **kwargs,
    ):
        self._style = style
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        h = self._body_height
        stroke_color = self._stroke
        stroke_width = self._stroke_width
        fill_color = self._fill

        if self._style == "european":
            rect_width = w * 0.7
            rect_x = (w - rect_width) / 2
            rect_height = h * 0.6

            shapes.block(
                parent=self,
                ll=(rect_x, h / 2 + rect_height / 2),
                width=rect_width,
                height=rect_height,
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=stroke_width,
            )

            Line(
                parent=self,
                start_point=(-self._terminal_length, h / 2),
                points=[f"R{self._terminal_length + rect_x}"],
                width=stroke_width,
                color=stroke_color,
            )

            Line(
                parent=self,
                start_point=(rect_x + rect_width, h / 2),
                points=[f"R{self._terminal_length + rect_x}"],
                width=stroke_width,
                color=stroke_color,
            )
        else:
            zigzag_width = w * 0.7
            lead_length = (w - zigzag_width) / 2
            num_zigs = 6
            zig_w = zigzag_width / num_zigs
            zig_h = h / 2

            points = []
            points.append(f"R{lead_length + self._terminal_length}")
            for i in range(num_zigs):
                half_zig = zig_w / 2
                if i % 2 == 0:
                    points.append(f"R{half_zig}:U{zig_h}")
                    points.append(f"R{half_zig}:D{zig_h}")
                else:
                    points.append(f"R{half_zig}:D{zig_h}")
                    points.append(f"R{half_zig}:U{zig_h}")
            points.append(f"R{lead_length + self._terminal_length}")

            Line(
                parent=self,
                start_point=(-self._terminal_length, h / 2),
                points=points,
                width=stroke_width,
                color=stroke_color,
            )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + 10),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def terminal_left(self) -> Point:
        return Point(-self._terminal_length, self._body_height / 2)

    @property
    def terminal_right(self) -> Point:
        return Point(self._body_width + self._terminal_length, self._body_height / 2)


class Capacitor(Diagram):
    """Capacitor symbol - vertical orientation with terminals top and bottom."""

    def __init__(
        self,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        plate_width: float = 30,
        gap: float = 9,
        terminal_length: float = 15,
        **kwargs,
    ):
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._plate_width = plate_width
        self._gap = gap
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        pw = self._plate_width
        gap = self._gap
        stroke_color = self._stroke
        stroke_width = self._stroke_width
        term_len = self._terminal_length

        center_x = pw / 2
        top_plate_y = term_len
        bottom_plate_y = term_len + gap

        # Top plate (horizontal line)
        Line(
            parent=self,
            start_point=(0, top_plate_y),
            points=[f"R{pw}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Bottom plate (horizontal line)
        Line(
            parent=self,
            start_point=(0, bottom_plate_y),
            points=[f"R{pw}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Top terminal
        Line(
            parent=self,
            start_point=(center_x, 0),
            points=[f"D{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Bottom terminal
        Line(
            parent=self,
            start_point=(center_x, bottom_plate_y),
            points=[f"D{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(pw / 2, bottom_plate_y + term_len + 10),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def terminal_top(self) -> Point:
        return Point(self._plate_width / 2, 0)

    @property
    def terminal_bottom(self) -> Point:
        return Point(self._plate_width / 2, self._terminal_length * 2 + self._gap)


class Battery(Diagram):
    """Battery symbol - vertical orientation with terminals top and bottom.

    The negative terminal (long plate) is at the top, positive (short plate) at bottom.
    """

    def __init__(
        self,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        long_plate_width: float = 30,
        short_plate_width: float = 16,
        gap: float = 12,
        terminal_length: float = 15,
        **kwargs,
    ):
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._long_plate_width = long_plate_width
        self._short_plate_width = short_plate_width
        self._gap = gap
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        long_w = self._long_plate_width
        short_w = self._short_plate_width
        gap = self._gap
        stroke_color = self._stroke
        stroke_width = self._stroke_width
        term_len = self._terminal_length

        center_x = long_w / 2
        long_plate_y = term_len
        short_plate_y = term_len + gap

        # Long plate (negative, top)
        Line(
            parent=self,
            start_point=(0, long_plate_y),
            points=[f"R{long_w}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Short plate (positive, bottom) - thicker
        short_offset = (long_w - short_w) / 2
        Line(
            parent=self,
            start_point=(short_offset, short_plate_y),
            points=[f"R{short_w}"],
            width=stroke_width * 1.5,
            color=stroke_color,
        )

        # Top terminal (to negative)
        Line(
            parent=self,
            start_point=(center_x, 0),
            points=[f"D{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Bottom terminal (from positive)
        Line(
            parent=self,
            start_point=(center_x, short_plate_y),
            points=[f"D{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(long_w / 2, short_plate_y + term_len + 10),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def terminal_top(self) -> Point:
        """Negative terminal."""
        return Point(self._long_plate_width / 2, 0)

    @property
    def terminal_bottom(self) -> Point:
        """Positive terminal."""
        return Point(self._long_plate_width / 2, self._terminal_length * 2 + self._gap)
