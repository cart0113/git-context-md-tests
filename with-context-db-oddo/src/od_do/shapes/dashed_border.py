"""
Dashed border wrapper shape for OD-DO.

Wraps any existing shape and draws a dashed rectangular border around it
with configurable margin.

Example:
    from od_do.shapes.base import Rectangle
    from od_do.shapes.dashed_border import DashedBorder

    rect = Rectangle(parent=diagram, ll=(100, 200), width=50, height=30, fill="#ff0000",
                     stroke="#000000", stroke_width=1)
    border = DashedBorder(parent=diagram, child=rect, margin=15)
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram


class DashedBorder:
    """A dashed rectangular border that wraps any existing shape.

    The border is drawn around the child shape's bounding box with the
    specified margin. The child shape remains accessible via the `.child`
    attribute, and its anchor points continue to work normally.
    """

    def __init__(
        self,
        parent: "Diagram",
        child,
        margin: float = 10,
        stroke: Optional[ColorLike] = None,
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
        return self.child.x - self.margin

    @property
    def y(self) -> float:
        return self.child.y - self.margin

    @property
    def width(self) -> float:
        return self.child.width + 2 * self.margin

    @property
    def height(self) -> float:
        return self.child.height + 2 * self.margin

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

    @property
    def stroke_color(self) -> Optional[str]:
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke
