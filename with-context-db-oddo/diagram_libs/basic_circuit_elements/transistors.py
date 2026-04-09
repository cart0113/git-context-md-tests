"""Transistor, inductor, ground, and power circuit elements.

Classes: NMOS, PMOS, Inductor, Ground, VDD
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from od_do.diagram.base import Diagram
from od_do import shapes, colors
from od_do.shapes import text, curves
from od_do.shapes.curves import BezierPath
from od_do.paths import Line
from od_do.geometry import Point
from od_do.colors import ColorLike, Color

if TYPE_CHECKING:
    pass


class NMOS(Diagram):
    """NMOS enhancement-mode transistor.

    Vertical channel with gate on left, drain on top, source on bottom.
    Arrow on source points INTO the channel (NMOS convention).
    """

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        body_width: float = 40,
        body_height: float = 60,
        terminal_length: float = 15,
        **kwargs,
    ):
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
        term_len = self._terminal_length

        channel_x = w * 0.6
        gate_plate_x = w * 0.35
        gate_gap = w * 0.08
        channel_top = h * 0.15
        channel_bottom = h * 0.85
        channel_mid = h / 2

        # Channel line (vertical, right side)
        Line(
            parent=self,
            start_point=(channel_x, channel_top),
            points=[f"D{channel_bottom - channel_top}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Gate plate (vertical line parallel to channel)
        Line(
            parent=self,
            start_point=(gate_plate_x, channel_top),
            points=[f"D{channel_bottom - channel_top}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Gate terminal (horizontal line from left to gate plate)
        Line(
            parent=self,
            start_point=(-term_len, channel_mid),
            points=[f"R{term_len + gate_plate_x}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Drain connection (horizontal from channel to right, then up)
        Line(
            parent=self,
            start_point=(channel_x, channel_top),
            points=[f"R{w - channel_x}"],
            width=stroke_width,
            color=stroke_color,
        )
        Line(
            parent=self,
            start_point=(w, channel_top),
            points=[f"U{channel_top + term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Source connection (horizontal from channel to right, then down)
        Line(
            parent=self,
            start_point=(channel_x, channel_bottom),
            points=[f"R{w - channel_x}"],
            width=stroke_width,
            color=stroke_color,
        )
        Line(
            parent=self,
            start_point=(w, channel_bottom),
            points=[f"D{h - channel_bottom + term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Arrow on source pointing INTO channel (leftward arrow on source horizontal)
        arrow_size = 6
        arrow_tip_x = channel_x
        arrow_tip_y = channel_bottom
        BezierPath(
            parent=self,
            d=(
                f"M {arrow_tip_x},{arrow_tip_y} "
                f"L {arrow_tip_x + arrow_size},{arrow_tip_y - arrow_size * 0.6} "
                f"L {arrow_tip_x + arrow_size},{arrow_tip_y + arrow_size * 0.6} Z"
            ),
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + term_len + 10),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def gate_pin(self) -> Point:
        return Point(-self._terminal_length, self._body_height / 2)

    @property
    def drain_pin(self) -> Point:
        return Point(self._body_width, -self._terminal_length)

    @property
    def source_pin(self) -> Point:
        return Point(self._body_width, self._body_height + self._terminal_length)


class PMOS(Diagram):
    """PMOS enhancement-mode transistor.

    Same as NMOS but arrow on source points AWAY from channel,
    and a bubble on the gate indicates P-type.
    """

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        body_width: float = 40,
        body_height: float = 60,
        terminal_length: float = 15,
        **kwargs,
    ):
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
        term_len = self._terminal_length

        channel_x = w * 0.6
        gate_plate_x = w * 0.35
        channel_top = h * 0.15
        channel_bottom = h * 0.85
        channel_mid = h / 2
        bubble_r = 4

        # Channel line (vertical, right side)
        Line(
            parent=self,
            start_point=(channel_x, channel_top),
            points=[f"D{channel_bottom - channel_top}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Gate plate (vertical line parallel to channel)
        Line(
            parent=self,
            start_point=(gate_plate_x, channel_top),
            points=[f"D{channel_bottom - channel_top}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Gate bubble (circle between gate terminal and gate plate)
        bubble_cx = gate_plate_x - bubble_r
        shapes.Circle(
            parent=self,
            center=(bubble_cx, channel_mid),
            radius=bubble_r,
            fill=colors.WHITE,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Gate terminal (horizontal line from left to bubble)
        Line(
            parent=self,
            start_point=(-term_len, channel_mid),
            points=[f"R{term_len + bubble_cx - bubble_r}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Drain connection (horizontal from channel to right, then up)
        Line(
            parent=self,
            start_point=(channel_x, channel_top),
            points=[f"R{w - channel_x}"],
            width=stroke_width,
            color=stroke_color,
        )
        Line(
            parent=self,
            start_point=(w, channel_top),
            points=[f"U{channel_top + term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Source connection (horizontal from channel to right, then down)
        Line(
            parent=self,
            start_point=(channel_x, channel_bottom),
            points=[f"R{w - channel_x}"],
            width=stroke_width,
            color=stroke_color,
        )
        Line(
            parent=self,
            start_point=(w, channel_bottom),
            points=[f"D{h - channel_bottom + term_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Arrow on source pointing AWAY from channel (rightward arrow)
        arrow_size = 6
        arrow_base_x = channel_x
        arrow_base_y = channel_bottom
        BezierPath(
            parent=self,
            d=(
                f"M {arrow_base_x + arrow_size},{arrow_base_y} "
                f"L {arrow_base_x},{arrow_base_y - arrow_size * 0.6} "
                f"L {arrow_base_x},{arrow_base_y + arrow_size * 0.6} Z"
            ),
            fill=stroke_color,
            stroke=stroke_color,
            stroke_width=1,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + term_len + 10),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="top",
            )

    @property
    def gate_pin(self) -> Point:
        return Point(-self._terminal_length, self._body_height / 2)

    @property
    def drain_pin(self) -> Point:
        return Point(self._body_width, -self._terminal_length)

    @property
    def source_pin(self) -> Point:
        return Point(self._body_width, self._body_height + self._terminal_length)


class Inductor(Diagram):
    """Inductor symbol - horizontal with semicircular bumps."""

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        body_width: float = 60,
        body_height: float = 20,
        terminal_length: float = 8,
        num_bumps: int = 4,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        self._num_bumps = num_bumps
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        h = self._body_height
        stroke_color = self._stroke
        stroke_width = self._stroke_width
        term_len = self._terminal_length
        num_bumps = self._num_bumps

        center_y = h / 2
        coil_width = w * 0.7
        lead_length = (w - coil_width) / 2
        bump_width = coil_width / num_bumps
        bump_radius = bump_width / 2

        # Left lead
        Line(
            parent=self,
            start_point=(-term_len, center_y),
            points=[f"R{term_len + lead_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Semicircular bumps (arcing upward)
        for i in range(num_bumps):
            bump_center_x = lead_length + bump_width * i + bump_radius
            curves.SemiCircle(
                parent=self,
                center=(bump_center_x, center_y),
                radius=bump_radius,
                direction="up",
                stroke=stroke_color,
                stroke_width=stroke_width,
            )

        # Right lead
        Line(
            parent=self,
            start_point=(lead_length + coil_width, center_y),
            points=[f"R{term_len + lead_length}"],
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


class Ground(Diagram):
    """Standard earth ground symbol.

    Three horizontal lines decreasing in width with a vertical terminal on top.
    """

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        body_width: float = 30,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._body_width = body_width
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        stroke_color = self._stroke
        stroke_width = self._stroke_width

        terminal_len = 15
        line_spacing = 6
        center_x = w / 2

        # Vertical terminal line
        Line(
            parent=self,
            start_point=(center_x, -terminal_len),
            points=[f"D{terminal_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Three horizontal lines, decreasing in width
        line_widths = [w, w * 0.6, w * 0.25]
        for i, lw in enumerate(line_widths):
            y = i * line_spacing
            x_start = center_x - lw / 2
            Line(
                parent=self,
                start_point=(x_start, y),
                points=[f"R{lw}"],
                width=stroke_width,
                color=stroke_color,
            )

    @property
    def terminal_top(self) -> Point:
        return Point(self._body_width / 2, -15)


class VDD(Diagram):
    """VDD/power supply symbol.

    Horizontal line at top with vertical line down to terminal.
    """

    def __init__(
        self,
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = "VDD",
        body_width: float = 30,
        **kwargs,
    ):
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._body_width = body_width
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        stroke_color = self._stroke
        stroke_width = self._stroke_width

        terminal_len = 15
        center_x = w / 2

        # Horizontal bar at top
        Line(
            parent=self,
            start_point=(0, 0),
            points=[f"R{w}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Vertical line down to terminal
        Line(
            parent=self,
            start_point=(center_x, 0),
            points=[f"D{terminal_len}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(center_x, -8),
                content=self._label,
                font_size=12,
                color=colors.BLACK,
                align="center",
                valign="bottom",
            )

    @property
    def terminal_bottom(self) -> Point:
        return Point(self._body_width / 2, 15)
