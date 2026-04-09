"""
Dashed border wrapper shape for OD-DO.

Wraps any existing shape and draws a dashed rectangular border around it
with configurable margin.
"""

from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

from .base import Shape
from ..colors import Color

if TYPE_CHECKING:
    from ..diagram.base import Diagram


class DashedBorder(Shape):
    """A dashed rectangular border drawn around an existing child shape.

    The border is positioned automatically based on the child's bounding box
    plus the specified margin. The child shape remains accessible via `.child`
    and its anchor points continue to work normally.

    Example:
        rect = Rectangle(parent=d, ll=(50, 50), width=100, height=60, fill="#ccc", stroke="black", stroke_width=1)
        border = DashedBorder(parent=d, child=rect, margin=15, stroke="red", stroke_width=2)
    """

    def __init__(
        self,
        parent: "Diagram",
        child: Shape,
        margin: float = 10,
        stroke: Optional[Union[str, Color]] = "black",
        stroke_width: float = 1,
    ):
        self.child = child
        self.margin = margin

        width = child.width + 2 * margin
        height = child.height + 2 * margin

        # Skip normal resolve_position — derive position from child directly
        self.parent = parent
        self.width = width
        self.height = height
        self.x = child.x - margin
        self.y = child.y - margin
        self.fill = None
        self.stroke = stroke
        self.stroke_width = stroke_width
        parent.add_shape(self)
