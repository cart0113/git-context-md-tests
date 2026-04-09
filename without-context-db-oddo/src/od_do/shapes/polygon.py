"""
Polygon shapes for OD-DO.

Provides regular polygons (triangle, pentagon, hexagon, etc.) and stars.
Uses SVG polygon element internally.

Example:
    from od_do.shapes import polygon
    from od_do import colors

    # Regular triangle
    tri = polygon.Triangle(
        parent=diagram,
        center=(100, 100),
        radius=50,
        fill=colors.YELLOW,
        stroke=colors.BLACK,
    )

    # Regular hexagon
    hex = polygon.Hexagon(
        parent=diagram,
        center=(200, 100),
        radius=40,
        fill=colors.LIGHT_BLUE,
    )

    # 5-pointed star
    star = polygon.Star(
        parent=diagram,
        center=(300, 100),
        outer_radius=50,
        inner_radius=20,
        points=5,
        fill=colors.GOLD,
    )
"""

from __future__ import annotations

import math
from typing import Optional, Union, Tuple, List, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


class RegularPolygon:
    """A regular polygon with equal sides and angles.

    Defined by center, radius (circumradius), and number of sides.
    Rotation angle can be specified to orient the polygon.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        sides: int,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 0,
    ):
        if sides < 3:
            raise ValueError("Polygon must have at least 3 sides")
        self.center = Point.resolve_point(center)
        self.radius = radius
        self.sides = sides
        self.rotation = rotation
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def vertices(self) -> List[Point]:
        result = []
        angle_step = 2 * math.pi / self.sides
        start_angle = math.radians(self.rotation) - math.pi / 2
        for i in range(self.sides):
            angle = start_angle + i * angle_step
            x = self.center.x + self.radius * math.cos(angle)
            y = self.center.y + self.radius * math.sin(angle)
            result.append(Point(x, y))
        return result

    @property
    def x(self) -> float:
        return min(v.x for v in self.vertices)

    @property
    def y(self) -> float:
        return min(v.y for v in self.vertices)

    @property
    def width(self) -> float:
        verts = self.vertices
        return max(v.x for v in verts) - min(v.x for v in verts)

    @property
    def height(self) -> float:
        verts = self.vertices
        return max(v.y for v in verts) - min(v.y for v in verts)

    @property
    def bbox(self) -> BBox:
        verts = self.vertices
        min_x = min(v.x for v in verts)
        max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts)
        max_y = max(v.y for v in verts)
        return BBox(ll=Point(min_x, max_y), ur=Point(max_x, min_y))

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

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    def svg_points(self) -> str:
        return " ".join(f"{v.x},{v.y}" for v in self.vertices)


class Triangle(RegularPolygon):
    """A regular triangle (equilateral).

    By default, one vertex points upward. Use rotation to orient differently.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 0,
    ):
        super().__init__(parent, center, radius, 3, fill, stroke, stroke_width, rotation)


class Pentagon(RegularPolygon):
    """A regular pentagon (5 sides)."""

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 0,
    ):
        super().__init__(parent, center, radius, 5, fill, stroke, stroke_width, rotation)


class Hexagon(RegularPolygon):
    """A regular hexagon (6 sides).

    By default, oriented with flat top. Use rotation=30 for pointy top.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 30,
    ):
        super().__init__(parent, center, radius, 6, fill, stroke, stroke_width, rotation)


class Octagon(RegularPolygon):
    """A regular octagon (8 sides)."""

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 22.5,
    ):
        super().__init__(parent, center, radius, 8, fill, stroke, stroke_width, rotation)


class Star:
    """A star shape with specified number of points.

    Defined by outer radius (tips), inner radius (valleys), and number of points.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        outer_radius: float,
        inner_radius: float,
        num_points: int,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        rotation: float = 0,
    ):
        if num_points < 3:
            raise ValueError("Star must have at least 3 points")
        self.center = Point.resolve_point(center)
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.num_points = num_points
        self.rotation = rotation
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def vertices(self) -> List[Point]:
        result = []
        angle_step = math.pi / self.num_points
        start_angle = math.radians(self.rotation) - math.pi / 2
        for i in range(self.num_points * 2):
            radius = self.outer_radius if i % 2 == 0 else self.inner_radius
            angle = start_angle + i * angle_step
            x = self.center.x + radius * math.cos(angle)
            y = self.center.y + radius * math.sin(angle)
            result.append(Point(x, y))
        return result

    @property
    def x(self) -> float:
        return self.center.x - self.outer_radius

    @property
    def y(self) -> float:
        return self.center.y - self.outer_radius

    @property
    def width(self) -> float:
        return self.outer_radius * 2

    @property
    def height(self) -> float:
        return self.outer_radius * 2

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.center.x - self.outer_radius, self.center.y + self.outer_radius),
            ur=Point(self.center.x + self.outer_radius, self.center.y - self.outer_radius),
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

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    def svg_points(self) -> str:
        return " ".join(f"{v.x},{v.y}" for v in self.vertices)
