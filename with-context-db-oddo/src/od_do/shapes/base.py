"""
Base shape classes for OD-DO.

Provides the Shape base class and concrete shape implementations (Rectangle, Circle, Block).
All shapes have a bounding box (bbox) and anchor points accessible via the points property.

Example:
    from od_do.shapes.base import Rectangle, Circle

    rect = Rectangle(parent=diagram, ll=(100, 200), width=50, height=30, fill="#ff0000")
    circ = Circle(parent=diagram, center=(150, 150), radius=25, fill="#00ff00")
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import Point, BBox, Points, PointLike, resolve_position
from ..colors import Color

if TYPE_CHECKING:
    from ..diagram.base import Diagram


class Shape:
    """Base class for all shapes.

    Shapes are the fundamental drawing primitives in OD-DO. Every shape has:
    - Position via corner points (ll, ul, lr, ur)
    - Size (width, height)
    - Styling (fill, stroke, stroke_width)
    - A bounding box (bbox property)
    - Anchor points (points property)

    Shapes automatically register themselves with their parent diagram.
    """

    def __init__(
        self,
        parent: "Diagram",
        width: float,
        height: float,
        fill: Optional[Union[str, Color]],
        stroke: Optional[Union[str, Color]],
        stroke_width: float,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
    ):
        self.parent = parent
        self.width = width
        self.height = height
        self.x, self.y = resolve_position(width, height, ll, ul, lr, ur)
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        parent.add_shape(self)

    @property
    def bbox(self) -> BBox:
        """Return the bounding box of this shape."""
        return BBox(
            ll=Point(self.x, self.y + self.height),
            ur=Point(self.x + self.width, self.y),
        )

    @property
    def points(self) -> Points:
        """Return anchor points helper for this shape."""
        return Points(self)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y) for this shape."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    @property
    def fill_color(self) -> Optional[str]:
        """Return fill color as a string suitable for SVG."""
        if self.fill is None:
            return None
        if isinstance(self.fill, Color):
            return self.fill.svg_color()
        return self.fill

    @property
    def stroke_color(self) -> Optional[str]:
        """Return stroke color as a string suitable for SVG."""
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def fill_opacity(self) -> Optional[float]:
        """Return fill opacity if fill is a Color with alpha < 1."""
        if isinstance(self.fill, Color) and self.fill.a < 1.0:
            return self.fill.a
        return None

    @property
    def stroke_opacity(self) -> Optional[float]:
        """Return stroke opacity if stroke is a Color with alpha < 1."""
        if isinstance(self.stroke, Color) and self.stroke.a < 1.0:
            return self.stroke.a
        return None


class Rectangle(Shape):
    """A rectangle shape with optional rounded corners."""

    def __init__(
        self,
        parent: "Diagram",
        width: float,
        height: float,
        fill: Optional[Union[str, Color]],
        stroke: Optional[Union[str, Color]],
        stroke_width: float,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
        corners: Optional[str] = None,
    ):
        super().__init__(parent, width, height, fill, stroke, stroke_width, ll, ul, lr, ur)
        self.corners = corners

    @property
    def corner_radius(self) -> Optional[float]:
        """Calculate the corner radius in pixels based on corners parameter."""
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


class Circle(Shape):
    """A circle shape defined by center or corner position and radius."""

    def __init__(
        self,
        parent: "Diagram",
        radius: float,
        fill: Optional[Union[str, Color]],
        stroke: Optional[Union[str, Color]],
        stroke_width: float,
        center: Optional[PointLike] = None,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
    ):
        diameter = radius * 2

        if center is not None:
            positions_specified = sum(
                [ll is not None, ul is not None, lr is not None, ur is not None]
            )
            if positions_specified > 0:
                raise ValueError("Cannot specify both center and corner position")
            if isinstance(center, Point):
                cx, cy = center.x, center.y
            else:
                cx, cy = center
            ul = (cx - radius, cy - radius)

        super().__init__(parent, diameter, diameter, fill, stroke, stroke_width, ll, ul, lr, ur)
        self.radius = radius


class Block(Rectangle):
    """A block shape (alias for Rectangle)."""

    pass


class OpenBlock(Shape):
    """A rectangle with stroke on only 3 sides (one side open)."""

    def __init__(
        self,
        parent: "Diagram",
        width: float,
        height: float,
        fill: Optional[Union[str, Color]],
        stroke: Optional[Union[str, Color]],
        stroke_width: float,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
        open_side: str = "right",
    ):
        super().__init__(parent, width, height, fill, stroke, stroke_width, ll, ul, lr, ur)
        self.open_side = open_side

    def svg_path(self) -> str:
        """Generate SVG path for the 3-sided stroke."""
        x, y, w, h = self.x, self.y, self.width, self.height

        if self.open_side == "right":
            return f"M {x + w},{y} L {x},{y} L {x},{y + h} L {x + w},{y + h}"
        elif self.open_side == "left":
            return f"M {x},{y} L {x + w},{y} L {x + w},{y + h} L {x},{y + h}"
        elif self.open_side == "top":
            return f"M {x},{y} L {x},{y + h} L {x + w},{y + h} L {x + w},{y}"
        elif self.open_side == "bottom":
            return f"M {x},{y + h} L {x},{y} L {x + w},{y} L {x + w},{y + h}"
        return ""
