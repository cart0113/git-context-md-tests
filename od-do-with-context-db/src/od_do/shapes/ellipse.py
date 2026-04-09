"""
Ellipse shape for OD-DO.

Provides the Ellipse class - a native SVG ellipse shape with independent
x and y radii.

Example:
    from od_do.shapes import ellipse
    from od_do import colors

    # Create an ellipse
    e = ellipse.Ellipse(
        parent=diagram,
        center=(200, 150),
        radius_x=80,
        radius_y=40,
        fill=colors.LIGHT_BLUE,
        stroke=colors.DARK_BLUE,
        stroke_width=2,
    )
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


class Ellipse:
    """An ellipse shape with independent x and y radii.

    Unlike Circle which has equal radii, Ellipse allows specifying
    different horizontal and vertical radii. Uses SVG ellipse element.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius_x: float,
        radius_y: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.center = Point.resolve_point(center)
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def x(self) -> float:
        return self.center.x - self.radius_x

    @property
    def y(self) -> float:
        return self.center.y - self.radius_y

    @property
    def width(self) -> float:
        return self.radius_x * 2

    @property
    def height(self) -> float:
        return self.radius_y * 2

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.center.x - self.radius_x, self.center.y + self.radius_y),
            ur=Point(self.center.x + self.radius_x, self.center.y - self.radius_y),
        )

    @property
    def points(self) -> Points:
        return Points(self)

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
    def fill_opacity(self) -> Optional[float]:
        if isinstance(self.fill, Color) and self.fill.a < 1.0:
            return self.fill.a
        return None

    @property
    def stroke_opacity(self) -> Optional[float]:
        if isinstance(self.stroke, Color) and self.stroke.a < 1.0:
            return self.stroke.a
        return None

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)
