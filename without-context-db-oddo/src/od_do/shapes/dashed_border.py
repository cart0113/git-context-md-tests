"""
DashedBorder shape for OD-DO.

Wraps any existing shape and draws a dashed rectangular border around it
with configurable margin.

Example:
    from od_do.shapes.base import Block
    from od_do.shapes.dashed_border import DashedBorder

    block = Block(parent=diagram, ll=(100, 200), width=50, height=30, fill="#ff0000",
                  stroke="#000000", stroke_width=1)
    border = DashedBorder(parent=diagram, child=block, margin=10, stroke="#333333")
"""

from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color

if TYPE_CHECKING:
    from ..diagram.base import Diagram
    from .base import Shape


class DashedBorder:
    """A dashed rectangular border drawn around a child shape.

    The border is positioned based on the child's bounding box plus a margin.
    The child shape remains accessible via the `.child` attribute, and its
    anchor points continue to work normally.
    """

    def __init__(
        self,
        parent: "Diagram",
        child: "Shape",
        margin: float = 10,
        stroke: Optional[Union[str, Color]] = "#000000",
        stroke_width: float = 1,
    ):
        self.parent = parent
        self.child = child
        self.margin = margin
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill = None

        # Compute position from child's bounding box plus margin
        child_bbox = child.bbox
        self.x = child.x - margin
        self.y = child.y - margin
        self.width = child.width + 2 * margin
        self.height = child.height + 2 * margin

        parent.add_shape(self)

    @property
    def bbox(self) -> BBox:
        """Return the bounding box of the dashed border."""
        return BBox(
            ll=Point(self.x, self.y + self.height),
            ur=Point(self.x + self.width, self.y),
        )

    @property
    def points(self) -> Points:
        """Return anchor points helper for the dashed border."""
        return Points(self)

    def bounding_box(self):
        """Return (min_x, min_y, max_x, max_y) for the dashed border."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    @property
    def fill_color(self) -> None:
        return None

    @property
    def stroke_color(self) -> Optional[str]:
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def fill_opacity(self) -> None:
        return None

    @property
    def stroke_opacity(self) -> Optional[float]:
        if isinstance(self.stroke, Color) and self.stroke.a < 1.0:
            return self.stroke.a
        return None
