"""
Annotation shapes for OD-DO.

Provides dimension lines, callouts, and leader lines for technical drawings.

Example:
    from od_do.shapes import annotations
    from od_do import colors

    # Dimension line (horizontal measurement)
    dim = annotations.DimensionLine(
        parent=diagram,
        start=(100, 200),
        end=(300, 200),
        offset=20,
        stroke=colors.BLACK,
    )

    # Leader line with callout
    leader = annotations.LeaderLine(
        parent=diagram,
        start=(150, 150),
        elbow=(200, 100),
        end=(250, 100),
        stroke=colors.DARK_GRAY,
    )

    # Callout (speech bubble)
    callout = annotations.Callout(
        parent=diagram,
        target=(200, 200),
        box_center=(300, 100),
        box_width=100,
        box_height=50,
        fill=colors.LIGHT_YELLOW,
        stroke=colors.BLACK,
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


class DimensionLine:
    """A dimension line for technical drawings.

    Shows a measurement line with extension lines and tick marks.
    The measurement runs from `start` to `end`, with the dimension line
    offset perpendicular to the measurement by `offset`.
    """

    def __init__(
        self,
        parent: "Diagram",
        start: PointLike,
        end: PointLike,
        offset: float = 20,
        extension: float = 5,
        tick_size: float = 6,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.start = Point.resolve_point(start)
        self.end = Point.resolve_point(end)
        self.offset = offset
        self.extension = extension
        self.tick_size = tick_size
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def _direction(self) -> Point:
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return Point(1, 0)
        return Point(dx / length, dy / length)

    @property
    def _perpendicular(self) -> Point:
        d = self._direction
        return Point(-d.y, d.x)

    @property
    def dimension_start(self) -> Point:
        p = self._perpendicular
        return Point(
            self.start.x + p.x * self.offset,
            self.start.y + p.y * self.offset,
        )

    @property
    def dimension_end(self) -> Point:
        p = self._perpendicular
        return Point(
            self.end.x + p.x * self.offset,
            self.end.y + p.y * self.offset,
        )

    @property
    def extension_line_start_inner(self) -> Point:
        return self.start

    @property
    def extension_line_start_outer(self) -> Point:
        p = self._perpendicular
        return Point(
            self.start.x + p.x * (self.offset + self.extension),
            self.start.y + p.y * (self.offset + self.extension),
        )

    @property
    def extension_line_end_inner(self) -> Point:
        return self.end

    @property
    def extension_line_end_outer(self) -> Point:
        p = self._perpendicular
        return Point(
            self.end.x + p.x * (self.offset + self.extension),
            self.end.y + p.y * (self.offset + self.extension),
        )

    @property
    def x(self) -> float:
        pts = [
            self.start,
            self.end,
            self.dimension_start,
            self.dimension_end,
            self.extension_line_start_outer,
            self.extension_line_end_outer,
        ]
        return min(p.x for p in pts)

    @property
    def y(self) -> float:
        pts = [
            self.start,
            self.end,
            self.dimension_start,
            self.dimension_end,
            self.extension_line_start_outer,
            self.extension_line_end_outer,
        ]
        return min(p.y for p in pts)

    @property
    def width(self) -> float:
        pts = [
            self.start,
            self.end,
            self.dimension_start,
            self.dimension_end,
            self.extension_line_start_outer,
            self.extension_line_end_outer,
        ]
        return max(p.x for p in pts) - min(p.x for p in pts)

    @property
    def height(self) -> float:
        pts = [
            self.start,
            self.end,
            self.dimension_start,
            self.dimension_end,
            self.extension_line_start_outer,
            self.extension_line_end_outer,
        ]
        return max(p.y for p in pts) - min(p.y for p in pts)

    @property
    def bbox(self) -> BBox:
        pts = [
            self.start,
            self.end,
            self.dimension_start,
            self.dimension_end,
            self.extension_line_start_outer,
            self.extension_line_end_outer,
        ]
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return BBox(ll=Point(min_x, max_y), ur=Point(max_x, min_y))

    @property
    def points(self) -> Points:
        return Points(self)

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

    def length(self) -> float:
        return self.start.distance_to(self.end)


class LeaderLine:
    """A leader line for annotations.

    A line from a target point, through an optional elbow, to an endpoint.
    Commonly used with callouts or labels.
    """

    def __init__(
        self,
        parent: "Diagram",
        start: PointLike,
        end: PointLike,
        elbow: Optional[PointLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        arrow_size: float = 8,
    ):
        self.start = Point.resolve_point(start)
        self.end = Point.resolve_point(end)
        self.elbow = Point.resolve_point(elbow) if elbow else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.arrow_size = arrow_size
        self.parent = parent
        parent.add_shape(self)

    @property
    def path_points(self) -> List[Point]:
        if self.elbow:
            return [self.start, self.elbow, self.end]
        return [self.start, self.end]

    @property
    def x(self) -> float:
        pts = self.path_points
        return min(p.x for p in pts)

    @property
    def y(self) -> float:
        pts = self.path_points
        return min(p.y for p in pts)

    @property
    def width(self) -> float:
        pts = self.path_points
        return max(p.x for p in pts) - min(p.x for p in pts)

    @property
    def height(self) -> float:
        pts = self.path_points
        return max(p.y for p in pts) - min(p.y for p in pts)

    @property
    def bbox(self) -> BBox:
        pts = self.path_points
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)
        return BBox(ll=Point(min_x, max_y), ur=Point(max_x, min_y))

    @property
    def points(self) -> Points:
        return Points(self)

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


class Callout:
    """A callout shape (speech bubble) with a pointer.

    A rounded rectangle with a triangular pointer extending toward a target point.
    """

    def __init__(
        self,
        parent: "Diagram",
        target: PointLike,
        box_center: PointLike,
        box_width: float,
        box_height: float,
        pointer_width: float = 15,
        corner_radius: float = 5,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.target = Point.resolve_point(target)
        self.box_center = Point.resolve_point(box_center)
        self.box_width = box_width
        self.box_height = box_height
        self.pointer_width = pointer_width
        self.corner_radius = corner_radius
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def box_left(self) -> float:
        return self.box_center.x - self.box_width / 2

    @property
    def box_right(self) -> float:
        return self.box_center.x + self.box_width / 2

    @property
    def box_top(self) -> float:
        return self.box_center.y - self.box_height / 2

    @property
    def box_bottom(self) -> float:
        return self.box_center.y + self.box_height / 2

    @property
    def x(self) -> float:
        return min(self.box_left, self.target.x)

    @property
    def y(self) -> float:
        return min(self.box_top, self.target.y)

    @property
    def width(self) -> float:
        return max(self.box_right, self.target.x) - self.x

    @property
    def height(self) -> float:
        return max(self.box_bottom, self.target.y) - self.y

    @property
    def bbox(self) -> BBox:
        min_x = min(self.box_left, self.target.x)
        max_x = max(self.box_right, self.target.x)
        min_y = min(self.box_top, self.target.y)
        max_y = max(self.box_bottom, self.target.y)
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

    def _pointer_edge(self) -> str:
        dx = self.target.x - self.box_center.x
        dy = self.target.y - self.box_center.y
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "bottom" if dy > 0 else "top"

    def _pointer_base_points(self) -> Tuple[Point, Point]:
        edge = self._pointer_edge()
        half_width = self.pointer_width / 2
        if edge == "bottom":
            cx = max(self.box_left + self.corner_radius, min(self.target.x, self.box_right - self.corner_radius))
            return (Point(cx - half_width, self.box_bottom), Point(cx + half_width, self.box_bottom))
        elif edge == "top":
            cx = max(self.box_left + self.corner_radius, min(self.target.x, self.box_right - self.corner_radius))
            return (Point(cx - half_width, self.box_top), Point(cx + half_width, self.box_top))
        elif edge == "right":
            cy = max(self.box_top + self.corner_radius, min(self.target.y, self.box_bottom - self.corner_radius))
            return (Point(self.box_right, cy - half_width), Point(self.box_right, cy + half_width))
        else:
            cy = max(self.box_top + self.corner_radius, min(self.target.y, self.box_bottom - self.corner_radius))
            return (Point(self.box_left, cy - half_width), Point(self.box_left, cy + half_width))

    def svg_path(self) -> str:
        r = self.corner_radius
        l, t, ri, b = self.box_left, self.box_top, self.box_right, self.box_bottom
        edge = self._pointer_edge()
        p1, p2 = self._pointer_base_points()

        if edge == "bottom":
            return (
                f"M {l + r},{t} "
                f"L {ri - r},{t} Q {ri},{t} {ri},{t + r} "
                f"L {ri},{b - r} Q {ri},{b} {ri - r},{b} "
                f"L {p2.x},{b} L {self.target.x},{self.target.y} L {p1.x},{b} "
                f"L {l + r},{b} Q {l},{b} {l},{b - r} "
                f"L {l},{t + r} Q {l},{t} {l + r},{t} Z"
            )
        elif edge == "top":
            return (
                f"M {l + r},{t} "
                f"L {p1.x},{t} L {self.target.x},{self.target.y} L {p2.x},{t} "
                f"L {ri - r},{t} Q {ri},{t} {ri},{t + r} "
                f"L {ri},{b - r} Q {ri},{b} {ri - r},{b} "
                f"L {l + r},{b} Q {l},{b} {l},{b - r} "
                f"L {l},{t + r} Q {l},{t} {l + r},{t} Z"
            )
        elif edge == "right":
            return (
                f"M {l + r},{t} "
                f"L {ri - r},{t} Q {ri},{t} {ri},{t + r} "
                f"L {ri},{p1.y} L {self.target.x},{self.target.y} L {ri},{p2.y} "
                f"L {ri},{b - r} Q {ri},{b} {ri - r},{b} "
                f"L {l + r},{b} Q {l},{b} {l},{b - r} "
                f"L {l},{t + r} Q {l},{t} {l + r},{t} Z"
            )
        else:
            return (
                f"M {l + r},{t} "
                f"L {ri - r},{t} Q {ri},{t} {ri},{t + r} "
                f"L {ri},{b - r} Q {ri},{b} {ri - r},{b} "
                f"L {l + r},{b} Q {l},{b} {l},{b - r} "
                f"L {l},{p2.y} L {self.target.x},{self.target.y} L {l},{p1.y} "
                f"L {l},{t + r} Q {l},{t} {l + r},{t} Z"
            )
