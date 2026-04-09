"""
Text shapes for OD-DO.

Provides text rendering with alignment, multi-line support, and text boxes.

Alignment options:
- horizontal: "left", "center", "right"
- vertical: "top", "middle", "bottom"

Example:
    from od_do.shapes import text
    from od_do import colors

    # Simple text
    text.Text(
        parent=diagram,
        position=(100, 100),
        content="Hello World",
        font_size=16,
        color=colors.BLACK,
    )

    # Centered text in a box
    text.TextBox(
        parent=diagram,
        ll=(100, 200),
        width=150,
        height=50,
        content="Centered",
        align="center",
        valign="middle",
        fill=colors.LIGHT_BLUE,
        stroke=colors.DARK_BLUE,
    )

    # Label (text with optional background)
    text.Label(
        parent=diagram,
        position=(200, 100),
        content="Label",
        padding=5,
        fill=colors.LIGHT_YELLOW,
    )
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, List, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


ALIGN_TO_ANCHOR = {
    "left": "start",
    "center": "middle",
    "right": "end",
}

VALIGN_TO_BASELINE = {
    "top": "hanging",
    "middle": "central",
    "bottom": "text-after-edge",
}


class Text:
    """A text element at a specific position.

    The position is the anchor point, controlled by align and valign.
    """

    def __init__(
        self,
        parent: "Diagram",
        position: PointLike,
        content: str,
        font_size: float = 14,
        font_family: str = "sans-serif",
        font_weight: str = "normal",
        color: Optional[ColorLike] = None,
        align: str = "left",
        valign: str = "top",
        line_height: Optional[float] = None,
    ):
        self.position = Point.resolve_point(position)
        self.content = content
        self.font_size = font_size
        self.font_family = font_family
        self.font_weight = font_weight
        self.color = Color.resolve_color(color) if color is not None else Color("#000000")
        self.align = align
        self.valign = valign
        self.line_height = line_height if line_height is not None else font_size * 1.2
        self.parent = parent
        parent.add_shape(self)

    @property
    def lines(self) -> List[str]:
        return self.content.split("\n")

    @property
    def text_anchor(self) -> str:
        return ALIGN_TO_ANCHOR.get(self.align, "start")

    @property
    def dominant_baseline(self) -> str:
        return VALIGN_TO_BASELINE.get(self.valign, "hanging")

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    @property
    def width(self) -> float:
        max_len = max(len(line) for line in self.lines) if self.lines else 0
        return max_len * self.font_size * 0.6

    @property
    def height(self) -> float:
        return len(self.lines) * self.line_height

    @property
    def bbox(self) -> BBox:
        w, h = self.width, self.height
        x, y = self.position.x, self.position.y
        if self.align == "center":
            x -= w / 2
        elif self.align == "right":
            x -= w
        if self.valign == "middle":
            y -= h / 2
        elif self.valign == "bottom":
            y -= h
        return BBox(ll=Point(x, y + h), ur=Point(x + w, y))

    @property
    def points(self) -> Points:
        return Points(self)

    @property
    def fill_color(self) -> Optional[str]:
        if self.color is None:
            return None
        if isinstance(self.color, Color):
            return self.color.svg_color()
        return self.color

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)


class TextBox:
    """A rectangular box with text inside.

    Text is aligned within the box according to align and valign parameters.
    The box can have fill and stroke styling like a regular block.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        width: float,
        height: float,
        content: str,
        font_size: float = 14,
        font_family: str = "sans-serif",
        font_weight: str = "normal",
        text_color: Optional[ColorLike] = None,
        align: str = "center",
        valign: str = "middle",
        padding: float = 5,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        corners: Optional[str] = None,
        line_height: Optional[float] = None,
    ):
        self._ll = Point.resolve_point(ll)
        self._width = width
        self._height = height
        self.content = content
        self.font_size = font_size
        self.font_family = font_family
        self.font_weight = font_weight
        self.text_color = Color.resolve_color(text_color) if text_color is not None else Color("#000000")
        self.align = align
        self.valign = valign
        self.padding = padding
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.corners = corners
        self.line_height = line_height if line_height is not None else font_size * 1.2
        self.parent = parent
        parent.add_shape(self)

    @property
    def lines(self) -> List[str]:
        return self.content.split("\n")

    @property
    def x(self) -> float:
        return self._ll.x

    @property
    def y(self) -> float:
        return self._ll.y - self._height

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y),
            ur=Point(self._ll.x + self._width, self._ll.y - self._height),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    @property
    def corner_radius(self) -> Optional[float]:
        if self.corners is None:
            return None
        min_dim = min(self._width, self._height)
        if self.corners == "slightly-round":
            return min_dim * 0.05
        elif self.corners == "round":
            return min_dim * 0.1
        elif self.corners == "very-round":
            return min_dim * 0.2
        elif self.corners.startswith("round:"):
            factor = float(self.corners.split(":")[1])
            return min_dim * factor
        return None

    @property
    def text_x(self) -> float:
        if self.align == "left":
            return self._ll.x + self.padding
        elif self.align == "right":
            return self._ll.x + self._width - self.padding
        else:
            return self._ll.x + self._width / 2

    @property
    def text_y(self) -> float:
        num_lines = len(self.lines)
        total_text_height = num_lines * self.line_height
        box_top = self._ll.y - self._height

        if self.valign == "top":
            return box_top + self.padding + self.font_size * 0.8
        elif self.valign == "bottom":
            return self._ll.y - self.padding - (num_lines - 1) * self.line_height
        else:
            center_y = box_top + self._height / 2
            return center_y - total_text_height / 2 + self.font_size * 0.8

    @property
    def text_anchor(self) -> str:
        return ALIGN_TO_ANCHOR.get(self.align, "middle")

    @property
    def fill_color(self) -> Optional[str]:
        if self.fill is None:
            return None
        if isinstance(self.fill, Color):
            return self.fill.svg_color()
        return self.fill

    @property
    def stroke_color(self) -> Optional[str]:
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def text_fill_color(self) -> str:
        if isinstance(self.text_color, Color):
            return self.text_color.svg_color()
        return self.text_color

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)


class Label:
    """A text label with optional background.

    Unlike TextBox, Label auto-sizes to fit content with padding.
    Position is the anchor point of the text.
    """

    def __init__(
        self,
        parent: "Diagram",
        position: PointLike,
        content: str,
        font_size: float = 12,
        font_family: str = "sans-serif",
        font_weight: str = "normal",
        text_color: Optional[ColorLike] = None,
        align: str = "left",
        valign: str = "top",
        padding: float = 4,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        corners: Optional[str] = None,
        line_height: Optional[float] = None,
    ):
        self.position = Point.resolve_point(position)
        self.content = content
        self.font_size = font_size
        self.font_family = font_family
        self.font_weight = font_weight
        self.text_color = Color.resolve_color(text_color) if text_color is not None else Color("#000000")
        self.align = align
        self.valign = valign
        self.padding = padding
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.corners = corners
        self.line_height = line_height if line_height is not None else font_size * 1.2
        self.parent = parent
        parent.add_shape(self)

    @property
    def lines(self) -> List[str]:
        return self.content.split("\n")

    @property
    def text_width(self) -> float:
        max_len = max(len(line) for line in self.lines) if self.lines else 0
        return max_len * self.font_size * 0.6

    @property
    def text_height(self) -> float:
        return len(self.lines) * self.line_height

    @property
    def width(self) -> float:
        return self.text_width + self.padding * 2

    @property
    def height(self) -> float:
        return self.text_height + self.padding * 2

    @property
    def x(self) -> float:
        if self.align == "center":
            return self.position.x - self.width / 2
        elif self.align == "right":
            return self.position.x - self.width
        return self.position.x

    @property
    def y(self) -> float:
        if self.valign == "middle":
            return self.position.y - self.height / 2
        elif self.valign == "bottom":
            return self.position.y - self.height
        return self.position.y

    @property
    def box_x(self) -> float:
        return self.x

    @property
    def box_y(self) -> float:
        return self.y

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.x, self.y + self.height),
            ur=Point(self.x + self.width, self.y),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    @property
    def corner_radius(self) -> Optional[float]:
        if self.corners is None:
            return None
        min_dim = min(self.width, self.height)
        if self.corners == "slightly-round":
            return min_dim * 0.05
        elif self.corners == "round":
            return min_dim * 0.1
        elif self.corners == "very-round":
            return min_dim * 0.2
        elif self.corners.startswith("round:"):
            factor = float(self.corners.split(":")[1])
            return min_dim * factor
        return None

    @property
    def text_x(self) -> float:
        if self.align == "left":
            return self.x + self.padding
        elif self.align == "right":
            return self.x + self.width - self.padding
        else:
            return self.x + self.width / 2

    @property
    def text_y(self) -> float:
        return self.y + self.padding + self.font_size * 0.8

    @property
    def text_anchor(self) -> str:
        return ALIGN_TO_ANCHOR.get(self.align, "start")

    @property
    def fill_color(self) -> Optional[str]:
        if self.fill is None:
            return None
        if isinstance(self.fill, Color):
            return self.fill.svg_color()
        return self.fill

    @property
    def stroke_color(self) -> Optional[str]:
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def text_fill_color(self) -> str:
        if isinstance(self.text_color, Color):
            return self.text_color.svg_color()
        return self.text_color

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)
