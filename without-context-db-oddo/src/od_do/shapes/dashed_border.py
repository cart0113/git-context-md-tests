"""
DashedBorder shape for OD-DO.

Wraps any existing shape and draws a dashed rectangular border around it
with configurable margin.

Example:
    from od_do.shapes import dashed_border, Rectangle

    rect = Rectangle(parent=diagram, ll=(100, 100), width=80, height=60, fill="#ccc", stroke="#000", stroke_width=1)
    border = dashed_border.DashedBorder(
        parent=diagram,
        child=rect,
        margin=15,
        stroke="#333",
        stroke_width=2,
    )
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import BBox, Point, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram


class DashedBorder:
    """A dashed rectangular border drawn around a child shape.

    The border is positioned automatically based on the child's bounding box
    plus the given margin. The child shape remains accessible via the `.child`
    attribute, and its anchor points still work normally.
    """

    def __init__(
        self,
        parent: "Diagram",
        child,
        margin: float = 10,
        stroke: Optional[ColorLike] = "#000000",
        stroke_width: float = 1,
    ):
        self.parent = parent
        self.child = child
        self.margin = margin
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        parent.add_shape(self)

    @property
    def x(self) -> float:
        bb = self.child.bounding_box()
        return bb[0] - self.margin

    @property
    def y(self) -> float:
        bb = self.child.bounding_box()
        return bb[1] - self.margin

    @property
    def width(self) -> float:
        bb = self.child.bounding_box()
        return (bb[2] - bb[0]) + 2 * self.margin

    @property
    def height(self) -> float:
        bb = self.child.bounding_box()
        return (bb[3] - bb[1]) + 2 * self.margin

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.x, self.y + self.height),
            ur=Point(self.x + self.width, self.y),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)
