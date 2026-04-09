from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from od_do.diagram.base import Diagram
from od_do import shapes, colors
from od_do.shapes import curves, text
from od_do.shapes.curves import BezierPath
from od_do.paths import Line
from od_do.geometry import Point
from od_do.colors import ColorLike, Color

if TYPE_CHECKING:
    pass


class AND(Diagram):
    def __init__(
        self,
        num_inputs: int = 2,
        invert: bool = False,
        fill: Optional[ColorLike] = "#DFDFDF",
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        input_marker=None,
        output_marker=None,
        label: Optional[str] = None,
        label_color: Optional[ColorLike] = "#333333",
        body_width: float = 50,
        body_height: float = 60,
        terminal_length: float = 10,
        **kwargs,
    ):
        self.num_inputs = num_inputs
        self.invert = invert
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._input_marker = input_marker
        self._output_marker = output_marker
        self._label = label
        self._label_color = (
            Color.resolve_color(label_color) if label_color is not None else colors.BLACK
        )
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        w = self._body_width
        h = self._body_height
        arc_r = h / 2
        rect_width = w - arc_r

        fill_color = self._fill
        stroke_color = self._stroke
        stroke_width = self._stroke_width

        # Use OpenBlock for the body (open on right side to connect with semicircle)
        shapes.open_block(
            parent=self,
            ll=(0, h),
            width=rect_width,
            height=h,
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
            open_side="right",
        )

        # Semicircle for the rounded end
        curves.SemiCircle(
            parent=self,
            center=(rect_width, h / 2),
            radius=arc_r,
            direction="right",
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Input terminals
        spacing = h / (self.num_inputs + 1)
        for i in range(self.num_inputs):
            y = spacing * (i + 1)
            Line(
                parent=self,
                start_point=(-self._terminal_length, y),
                points=[f"R{self._terminal_length}"],
                width=stroke_width,
                color=stroke_color,
                start_marker=self._input_marker,
            )

        # Output terminal (with optional inversion bubble)
        output_x = w
        if self.invert:
            bubble_r = 5
            shapes.circle(
                parent=self,
                center=(w + bubble_r, h / 2),
                radius=bubble_r,
                fill=colors.WHITE,
                stroke=stroke_color,
                stroke_width=stroke_width,
            )
            output_x = w + bubble_r * 2

        Line(
            parent=self,
            start_point=(output_x, h / 2),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
            end_marker=self._output_marker,
        )

        # Label
        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + 18),
                content=self._label,
                font_size=14,
                color=self._label_color,
                align="center",
                valign="top",
            )

    def input_pin(self, index: int) -> Point:
        spacing = self._body_height / (self.num_inputs + 1)
        y = spacing * (index + 1)
        return Point(-self._terminal_length, y)

    @property
    def output_pin(self) -> Point:
        output_x = self._body_width
        if self.invert:
            bubble_r = 5
            output_x = self._body_width + bubble_r * 2
        return Point(output_x + self._terminal_length, self._body_height / 2)


class DFlipFlop(Diagram):
    def __init__(
        self,
        fill: Optional[ColorLike] = "#DFDFDF",
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        label_color: Optional[ColorLike] = "#333333",
        show_qbar: bool = False,
        show_labels: bool = False,
        body_width: float = 60,
        body_height: float = 80,
        terminal_length: float = 10,
        **kwargs,
    ):
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._label_color = (
            Color.resolve_color(label_color) if label_color is not None else colors.BLACK
        )
        self._show_qbar = show_qbar
        self._show_labels = show_labels
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

        # Main body rectangle
        shapes.block(
            parent=self,
            ll=(0, h),
            width=w,
            height=h,
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Input pins on left side
        d_y = h * 0.25
        clk_y = h * 0.75

        # D input
        Line(
            parent=self,
            start_point=(-self._terminal_length, d_y),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )
        if self._show_labels:
            text.Text(
                parent=self,
                position=(5, d_y),
                content="D",
                font_size=10,
                color=stroke_color,
                align="left",
                valign="middle",
            )

        # Clock input (with triangle)
        Line(
            parent=self,
            start_point=(-self._terminal_length, clk_y),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )
        # Clock triangle (bigger)
        tri_size = 12
        Line(
            parent=self,
            start_point=(0, clk_y - tri_size / 2),
            points=[f"R{tri_size}:D{tri_size / 2}", f"L{tri_size}:D{tri_size / 2}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Output pins on right side
        q_y = h * 0.25 if self._show_qbar else h / 2

        # Q output
        Line(
            parent=self,
            start_point=(w, q_y),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )
        if self._show_labels:
            text.Text(
                parent=self,
                position=(w - 5, q_y),
                content="Q",
                font_size=10,
                color=stroke_color,
                align="right",
                valign="middle",
            )

        # Q-bar output (optional)
        if self._show_qbar:
            qn_y = h * 0.75
            Line(
                parent=self,
                start_point=(w, qn_y),
                points=[f"R{self._terminal_length}"],
                width=stroke_width,
                color=stroke_color,
            )
            if self._show_labels:
                text.Text(
                    parent=self,
                    position=(w - 5, qn_y),
                    content="Q",
                    font_size=10,
                    color=stroke_color,
                    align="right",
                    valign="middle",
                )
                # Overline for Q-bar
                Line(
                    parent=self,
                    start_point=(w - 12, qn_y - 8),
                    points=["R8"],
                    width=stroke_width * 0.7,
                    color=stroke_color,
                )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + 18),
                content=self._label,
                font_size=14,
                color=self._label_color,
                align="center",
                valign="top",
            )

    @property
    def d_pin(self) -> Point:
        return Point(-self._terminal_length, self._body_height * 0.25)

    @property
    def clk_pin(self) -> Point:
        return Point(-self._terminal_length, self._body_height * 0.75)

    @property
    def q_pin(self) -> Point:
        q_y = self._body_height * 0.25 if self._show_qbar else self._body_height / 2
        return Point(self._body_width + self._terminal_length, q_y)

    @property
    def qn_pin(self) -> Point:
        return Point(self._body_width + self._terminal_length, self._body_height * 0.75)


class OR(Diagram):
    """OR gate with curved back and pointed front."""

    def __init__(
        self,
        num_inputs: int = 2,
        invert: bool = False,
        fill: Optional[ColorLike] = "#DFDFDF",
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        label_color: Optional[ColorLike] = "#333333",
        body_width: float = 50,
        body_height: float = 60,
        terminal_length: float = 10,
        **kwargs,
    ):
        self.num_inputs = num_inputs
        self.invert = invert
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._label_color = (
            Color.resolve_color(label_color) if label_color is not None else colors.BLACK
        )
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

        # OR gate shape using SVG path
        # Back curve indent amount (how much the back curves inward)
        back_indent = w * 0.2

        # Path: start at top-left, curve to bottom-left, curve to point, curve back to start
        # The side curves stay round longer before coming to point (like a "D" shape)
        path_d = (
            f"M 0,0 "
            f"Q {back_indent},{h/2} 0,{h} "  # Back curve (concave inward)
            f"Q {w*0.65},{h} {w},{h/2} "  # Bottom to point (stays full then curves to point)
            f"Q {w*0.65},0 0,0 "  # Point to top (stays full then curves back)
            f"Z"
        )

        BezierPath(
            parent=self,
            d=path_d,
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Input terminals - account for back curve
        spacing = h / (self.num_inputs + 1)
        for i in range(self.num_inputs):
            y = spacing * (i + 1)
            # Calculate x position where terminal meets the back curve
            # The back curve is a quadratic bezier from (0,0) to (0,h) with control at (back_indent, h/2)
            # At y position, x offset follows the curve
            t = y / h  # Parameter along curve (0 to 1)
            curve_x = 2 * t * (1 - t) * back_indent  # Quadratic bezier x at parameter t
            Line(
                parent=self,
                start_point=(-self._terminal_length, y),
                points=[f"R{self._terminal_length + curve_x}"],
                width=stroke_width,
                color=stroke_color,
            )

        # Output terminal (with optional inversion bubble)
        output_x = w
        if self.invert:
            bubble_r = 5
            shapes.circle(
                parent=self,
                center=(w + bubble_r, h / 2),
                radius=bubble_r,
                fill=colors.WHITE,
                stroke=stroke_color,
                stroke_width=stroke_width,
            )
            output_x = w + bubble_r * 2

        Line(
            parent=self,
            start_point=(output_x, h / 2),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + 18),
                content=self._label,
                font_size=14,
                color=self._label_color,
                align="center",
                valign="top",
            )

    def input_pin(self, index: int) -> Point:
        spacing = self._body_height / (self.num_inputs + 1)
        y = spacing * (index + 1)
        return Point(-self._terminal_length, y)

    @property
    def output_pin(self) -> Point:
        output_x = self._body_width
        if self.invert:
            bubble_r = 5
            output_x = self._body_width + bubble_r * 2
        return Point(output_x + self._terminal_length, self._body_height / 2)


class XOR(Diagram):
    """XOR gate - like OR but with extra curved line at input."""

    def __init__(
        self,
        num_inputs: int = 2,
        invert: bool = False,
        fill: Optional[ColorLike] = "#DFDFDF",
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        label_color: Optional[ColorLike] = "#333333",
        body_width: float = 50,
        body_height: float = 60,
        terminal_length: float = 10,
        **kwargs,
    ):
        self.num_inputs = num_inputs
        self.invert = invert
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._label_color = (
            Color.resolve_color(label_color) if label_color is not None else colors.BLACK
        )
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

        back_indent = w * 0.2
        xor_offset = 8  # Extra line offset

        # Main OR gate body (shifted right for XOR line)
        path_d = (
            f"M {xor_offset},0 "
            f"Q {xor_offset + back_indent},{h/2} {xor_offset},{h} "  # Back curve
            f"Q {xor_offset + w*0.65},{h} {xor_offset + w},{h/2} "  # Bottom to point
            f"Q {xor_offset + w*0.65},0 {xor_offset},0 "  # Point to top
            f"Z"
        )

        BezierPath(
            parent=self,
            d=path_d,
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Extra curved line at input (XOR identifier)
        xor_line_d = f"M 0,0 Q {back_indent},{h/2} 0,{h}"
        BezierPath(
            parent=self,
            d=xor_line_d,
            fill=None,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Input terminals
        spacing = h / (self.num_inputs + 1)
        for i in range(self.num_inputs):
            y = spacing * (i + 1)
            # Calculate x position where terminal meets the back curve
            t = y / h
            curve_x = 2 * t * (1 - t) * back_indent
            Line(
                parent=self,
                start_point=(-self._terminal_length, y),
                points=[f"R{self._terminal_length + curve_x}"],
                width=stroke_width,
                color=stroke_color,
            )

        # Output terminal
        output_x = xor_offset + w
        if self.invert:
            bubble_r = 5
            shapes.circle(
                parent=self,
                center=(output_x + bubble_r, h / 2),
                radius=bubble_r,
                fill=colors.WHITE,
                stroke=stroke_color,
                stroke_width=stroke_width,
            )
            output_x = output_x + bubble_r * 2

        Line(
            parent=self,
            start_point=(output_x, h / 2),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=((xor_offset + w) / 2, h + 18),
                content=self._label,
                font_size=14,
                color=self._label_color,
                align="center",
                valign="top",
            )

    def input_pin(self, index: int) -> Point:
        spacing = self._body_height / (self.num_inputs + 1)
        y = spacing * (index + 1)
        return Point(-self._terminal_length, y)

    @property
    def output_pin(self) -> Point:
        xor_offset = 8
        output_x = xor_offset + self._body_width
        if self.invert:
            bubble_r = 5
            output_x = output_x + bubble_r * 2
        return Point(output_x + self._terminal_length, self._body_height / 2)


class Buffer(Diagram):
    """Buffer gate - triangle shape."""

    def __init__(
        self,
        invert: bool = False,
        fill: Optional[ColorLike] = "#DFDFDF",
        stroke: Optional[ColorLike] = ("#707070", 0.9),
        stroke_width: float = 3.0,
        label: Optional[str] = None,
        label_color: Optional[ColorLike] = "#333333",
        body_width: float = 40,
        body_height: float = 50,
        terminal_length: float = 10,
        **kwargs,
    ):
        self.invert = invert
        self._fill = Color.resolve_color(fill) if fill is not None else None
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._label_color = (
            Color.resolve_color(label_color) if label_color is not None else colors.BLACK
        )
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

        # Triangle pointing right
        BezierPath(
            parent=self,
            d=f"M 0,0 L 0,{h} L {w},{h/2} Z",
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
        )

        # Input terminal
        Line(
            parent=self,
            start_point=(-self._terminal_length, h / 2),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        # Output terminal (with optional inversion bubble)
        output_x = w
        if self.invert:
            bubble_r = 5
            shapes.circle(
                parent=self,
                center=(w + bubble_r, h / 2),
                radius=bubble_r,
                fill=colors.WHITE,
                stroke=stroke_color,
                stroke_width=stroke_width,
            )
            output_x = w + bubble_r * 2

        Line(
            parent=self,
            start_point=(output_x, h / 2),
            points=[f"R{self._terminal_length}"],
            width=stroke_width,
            color=stroke_color,
        )

        if self._label:
            text.Text(
                parent=self,
                position=(w / 2, h + 18),
                content=self._label,
                font_size=14,
                color=self._label_color,
                align="center",
                valign="top",
            )

    @property
    def input_pin(self) -> Point:
        return Point(-self._terminal_length, self._body_height / 2)

    @property
    def output_pin(self) -> Point:
        output_x = self._body_width
        if self.invert:
            bubble_r = 5
            output_x = self._body_width + bubble_r * 2
        return Point(output_x + self._terminal_length, self._body_height / 2)
