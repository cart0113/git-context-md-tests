from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from od_do.diagram.base import Diagram
from od_do import shapes, colors
from od_do.shapes import curves
from od_do.paths import Line
from od_do.geometry import Point
from od_do.colors import ColorLike, Color

if TYPE_CHECKING:
    pass


class WireJump(Diagram):
    """A semicircle to indicate wire crossing over another wire."""

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        radius: float = 12,
        terminal_length: float = 10,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._radius = radius
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        r = self._radius
        stroke_color = self._stroke
        stroke_width = self._stroke_width
        term_len = self._terminal_length

        # Left lead into semicircle
        Line(
            parent=self,
            start_point=(-r - term_len, 0),
            points=[f"R{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Semicircle jump (arcs up)
        curves.SemiCircle(
            parent=self,
            center=(0, 0),
            radius=r,
            direction="up",
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Right lead from semicircle
        Line(
            parent=self,
            start_point=(r, 0),
            points=[f"R{term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

    @property
    def terminal_left(self) -> Point:
        return Point(-self._radius - self._terminal_length, 0)

    @property
    def terminal_right(self) -> Point:
        return Point(self._radius + self._terminal_length, 0)


class SwitchOpen(Diagram):
    """An open switch symbol."""

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        body_width: float = 40,
        body_height: float = 20,
        terminal_length: float = 10,
        label: Optional[str] = None,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        self._label = label
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        h = self._body_height
        stroke_color = self._stroke
        stroke_width = self._stroke_width

        # Left terminal and contact point
        Line(
            parent=self,
            start_point=(-self._terminal_length, h),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )
        shapes.Circle(
            parent=self,
            center=(0, h),
            radius=3,
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )

        # Lever (open position - angled up)
        Line(
            parent=self,
            start_point=(0, h),
            points=[f"R{w}:U{h * 0.8}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Right terminal and contact point
        shapes.Circle(
            parent=self,
            center=(w, h),
            radius=3,
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )
        Line(
            parent=self,
            start_point=(w, h),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            from od_do.shapes import text
            text.Text(
                parent=self,
                position=(w / 2, h + 15),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def terminal_left(self) -> Point:
        return Point(-self._terminal_length, self._body_height)

    @property
    def terminal_right(self) -> Point:
        return Point(self._body_width + self._terminal_length, self._body_height)


class SwitchClosed(Diagram):
    """A closed switch symbol."""

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        body_width: float = 40,
        body_height: float = 20,
        terminal_length: float = 10,
        label: Optional[str] = None,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        self._label = label
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        h = self._body_height
        stroke_color = self._stroke
        stroke_width = self._stroke_width

        # Left terminal and contact point
        Line(
            parent=self,
            start_point=(-self._terminal_length, h),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )
        shapes.Circle(
            parent=self,
            center=(0, h),
            radius=3,
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )

        # Lever (closed position - horizontal)
        Line(
            parent=self,
            start_point=(0, h),
            points=[f"R{w}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Right terminal and contact point
        shapes.Circle(
            parent=self,
            center=(w, h),
            radius=3,
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )
        Line(
            parent=self,
            start_point=(w, h),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            from od_do.shapes import text
            text.Text(
                parent=self,
                position=(w / 2, h + 15),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def terminal_left(self) -> Point:
        return Point(-self._terminal_length, self._body_height)

    @property
    def terminal_right(self) -> Point:
        return Point(self._body_width + self._terminal_length, self._body_height)


class Junction(Diagram):
    """A wire junction dot."""

    def __init__(
        self,
        fill: Optional[ColorLike] = ("#707070", 0.9),
        radius: float = 4,
        **kwargs,
    ):
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._radius = radius
        super().__init__(**kwargs)

    def draw(self):
        shapes.Circle(
            parent=self,
            center=(0, 0),
            radius=self._radius,
            fill=self._fill,
            stroke=None,
            stroke_width=0,
        )

    @property
    def center(self) -> Point:
        return Point(0, 0)
