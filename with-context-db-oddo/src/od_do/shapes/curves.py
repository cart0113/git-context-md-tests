"""
Curve shapes for OD-DO.

Provides Bezier curves (quadratic and cubic), arcs, and semi-circles.
Uses SVG path commands internally for rendering.

Example:
    from od_do.shapes import curves
    from od_do import colors

    # Quadratic Bezier curve
    quad = curves.QuadraticBezier(
        parent=diagram,
        start=(100, 200),
        control=(150, 100),
        end=(200, 200),
        stroke=colors.BLUE,
        stroke_width=2,
    )

    # Cubic Bezier curve
    cubic = curves.CubicBezier(
        parent=diagram,
        start=(100, 200),
        control1=(130, 100),
        control2=(170, 100),
        end=(200, 200),
        stroke=colors.RED,
        stroke_width=2,
    )

    # Arc
    arc = curves.Arc(
        parent=diagram,
        center=(200, 200),
        radius=50,
        start_angle=0,
        end_angle=180,
        stroke=colors.GREEN,
        stroke_width=2,
    )

    # Semi-circle
    semi = curves.SemiCircle(
        parent=diagram,
        center=(300, 200),
        radius=40,
        direction="up",
        stroke=colors.PURPLE,
        fill=colors.LIGHT_PURPLE,
    )
"""

from __future__ import annotations

import math
from typing import Optional, Union, Tuple, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


class CurveBase:
    """Base class for curve shapes.

    Curves are shapes defined by SVG path commands.
    All curves have a bounding box and points accessor.
    """

    def __init__(
        self,
        parent: "Diagram",
        stroke: Optional[ColorLike],
        stroke_width: float,
        fill: Optional[ColorLike] = None,
    ):
        self.parent = parent
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.fill = Color.resolve_color(fill) if fill is not None else None
        parent.add_shape(self)

    @property
    def stroke_color(self) -> Optional[str]:
        if self.stroke is None:
            return None
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def fill_color(self) -> Optional[str]:
        if self.fill is None:
            return None
        if isinstance(self.fill, Color):
            return self.fill.svg_color()
        return self.fill

    def svg_path(self) -> str:
        raise NotImplementedError

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)


class QuadraticBezier(CurveBase):
    """A quadratic Bezier curve with one control point.

    The curve starts at `start`, bends toward `control`, and ends at `end`.
    Uses SVG Q command internally.
    """

    def __init__(
        self,
        parent: "Diagram",
        start: PointLike,
        control: PointLike,
        end: PointLike,
        stroke: Optional[ColorLike],
        stroke_width: float = 1,
        fill: Optional[ColorLike] = None,
    ):
        self.start = Point.resolve_point(start)
        self.control = Point.resolve_point(control)
        self.end = Point.resolve_point(end)
        super().__init__(parent, stroke, stroke_width, fill)

    @property
    def x(self) -> float:
        return min(self.start.x, self.control.x, self.end.x)

    @property
    def y(self) -> float:
        return min(self.start.y, self.control.y, self.end.y)

    @property
    def width(self) -> float:
        return max(self.start.x, self.control.x, self.end.x) - self.x

    @property
    def height(self) -> float:
        return max(self.start.y, self.control.y, self.end.y) - self.y

    @property
    def bbox(self) -> BBox:
        min_x = min(self.start.x, self.control.x, self.end.x)
        max_x = max(self.start.x, self.control.x, self.end.x)
        min_y = min(self.start.y, self.control.y, self.end.y)
        max_y = max(self.start.y, self.control.y, self.end.y)
        return BBox(ll=Point(min_x, max_y), ur=Point(max_x, min_y))

    @property
    def points(self) -> Points:
        return Points(self)

    def svg_path(self) -> str:
        return (
            f"M {self.start.x},{self.start.y} "
            f"Q {self.control.x},{self.control.y} {self.end.x},{self.end.y}"
        )


class CubicBezier(CurveBase):
    """A cubic Bezier curve with two control points.

    The curve starts at `start`, bends toward `control1` and `control2`,
    and ends at `end`. Uses SVG C command internally.
    """

    def __init__(
        self,
        parent: "Diagram",
        start: PointLike,
        control1: PointLike,
        control2: PointLike,
        end: PointLike,
        stroke: Optional[ColorLike],
        stroke_width: float = 1,
        fill: Optional[ColorLike] = None,
    ):
        self.start = Point.resolve_point(start)
        self.control1 = Point.resolve_point(control1)
        self.control2 = Point.resolve_point(control2)
        self.end = Point.resolve_point(end)
        super().__init__(parent, stroke, stroke_width, fill)

    @property
    def x(self) -> float:
        return min(self.start.x, self.control1.x, self.control2.x, self.end.x)

    @property
    def y(self) -> float:
        return min(self.start.y, self.control1.y, self.control2.y, self.end.y)

    @property
    def width(self) -> float:
        return max(self.start.x, self.control1.x, self.control2.x, self.end.x) - self.x

    @property
    def height(self) -> float:
        return max(self.start.y, self.control1.y, self.control2.y, self.end.y) - self.y

    @property
    def bbox(self) -> BBox:
        min_x = min(self.start.x, self.control1.x, self.control2.x, self.end.x)
        max_x = max(self.start.x, self.control1.x, self.control2.x, self.end.x)
        min_y = min(self.start.y, self.control1.y, self.control2.y, self.end.y)
        max_y = max(self.start.y, self.control1.y, self.control2.y, self.end.y)
        return BBox(ll=Point(min_x, max_y), ur=Point(max_x, min_y))

    @property
    def points(self) -> Points:
        return Points(self)

    def svg_path(self) -> str:
        return (
            f"M {self.start.x},{self.start.y} "
            f"C {self.control1.x},{self.control1.y} "
            f"{self.control2.x},{self.control2.y} "
            f"{self.end.x},{self.end.y}"
        )


class Arc(CurveBase):
    """An arc (partial circle or ellipse).

    Defined by center, radius, start angle and end angle.
    Angles are in degrees, with 0 at 3 o'clock and increasing counter-clockwise.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        start_angle: float,
        end_angle: float,
        stroke: Optional[ColorLike],
        stroke_width: float = 1,
        fill: Optional[ColorLike] = None,
        radius_y: Optional[float] = None,
    ):
        self.center = Point.resolve_point(center)
        self.radius = radius
        self.radius_y = radius_y if radius_y is not None else radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        super().__init__(parent, stroke, stroke_width, fill)

    @property
    def x(self) -> float:
        return self.center.x - self.radius

    @property
    def y(self) -> float:
        return self.center.y - self.radius_y

    @property
    def width(self) -> float:
        return self.radius * 2

    @property
    def height(self) -> float:
        return self.radius_y * 2

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self.center.x - self.radius, self.center.y + self.radius_y),
            ur=Point(self.center.x + self.radius, self.center.y - self.radius_y),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    def _angle_to_point(self, angle: float) -> Point:
        rad = math.radians(angle)
        return Point(
            self.center.x + self.radius * math.cos(rad),
            self.center.y - self.radius_y * math.sin(rad),
        )

    def svg_path(self) -> str:
        start = self._angle_to_point(self.start_angle)
        end = self._angle_to_point(self.end_angle)

        angle_diff = (self.end_angle - self.start_angle) % 360
        large_arc = 1 if angle_diff > 180 else 0
        sweep = 0

        return (
            f"M {start.x},{start.y} "
            f"A {self.radius},{self.radius_y} 0 {large_arc},{sweep} {end.x},{end.y}"
        )


class SemiCircle(CurveBase):
    """A semi-circle (half circle).

    Convenience shape for creating half circles in different directions.
    """

    DIRECTIONS = ("up", "down", "left", "right")

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        radius: float,
        direction: str,
        stroke: Optional[ColorLike],
        stroke_width: float = 1,
        fill: Optional[ColorLike] = None,
    ):
        if direction not in self.DIRECTIONS:
            raise ValueError(f"direction must be one of {self.DIRECTIONS}")
        self.center = Point.resolve_point(center)
        self.radius = radius
        self.direction = direction
        super().__init__(parent, stroke, stroke_width, fill)

    @property
    def x(self) -> float:
        if self.direction == "right":
            return self.center.x
        return self.center.x - self.radius

    @property
    def y(self) -> float:
        if self.direction == "down":
            return self.center.y
        return self.center.y - self.radius

    @property
    def width(self) -> float:
        if self.direction in ("left", "right"):
            return self.radius
        return self.radius * 2

    @property
    def height(self) -> float:
        if self.direction in ("up", "down"):
            return self.radius
        return self.radius * 2

    @property
    def bbox(self) -> BBox:
        if self.direction == "up":
            return BBox(
                ll=Point(self.center.x - self.radius, self.center.y),
                ur=Point(self.center.x + self.radius, self.center.y - self.radius),
            )
        elif self.direction == "down":
            return BBox(
                ll=Point(self.center.x - self.radius, self.center.y + self.radius),
                ur=Point(self.center.x + self.radius, self.center.y),
            )
        elif self.direction == "left":
            return BBox(
                ll=Point(self.center.x - self.radius, self.center.y + self.radius),
                ur=Point(self.center.x, self.center.y - self.radius),
            )
        else:
            return BBox(
                ll=Point(self.center.x, self.center.y + self.radius),
                ur=Point(self.center.x + self.radius, self.center.y - self.radius),
            )

    @property
    def points(self) -> Points:
        return Points(self)

    def svg_path(self) -> str:
        r = self.radius
        cx, cy = self.center.x, self.center.y

        if self.direction == "up":
            return f"M {cx - r},{cy} A {r},{r} 0 0,1 {cx + r},{cy}"
        elif self.direction == "down":
            return f"M {cx - r},{cy} A {r},{r} 0 0,0 {cx + r},{cy}"
        elif self.direction == "left":
            return f"M {cx},{cy - r} A {r},{r} 0 0,0 {cx},{cy + r}"
        else:
            return f"M {cx},{cy - r} A {r},{r} 0 0,1 {cx},{cy + r}"


class BezierPath(CurveBase):
    """A general path defined by SVG path commands.

    Allows drawing arbitrary curved shapes using SVG path commands
    (M, L, Q, C, A, Z, etc.). Useful for shapes that can't be composed
    from simpler primitives.

    Example:
        # Draw a custom curved shape
        BezierPath(
            parent=diagram,
            d="M 0,0 Q 25,50 50,0 L 50,50 Q 25,0 0,50 Z",
            stroke=colors.BLACK,
            fill=colors.LIGHT_BLUE,
        )
    """

    def __init__(
        self,
        parent: "Diagram",
        d: str,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        fill: Optional[ColorLike] = None,
    ):
        """Create a path shape.

        Args:
            parent: The diagram to add this path to.
            d: SVG path data string (e.g., "M 0,0 L 50,50").
            stroke: Stroke color.
            stroke_width: Width of the stroke.
            fill: Fill color.
        """
        self.d = d
        self._bbox = self._parse_bbox(d)
        super().__init__(parent, stroke, stroke_width, fill)

    def _parse_bbox(self, d: str) -> BBox:
        """Parse path string to estimate bounding box."""
        import re

        # Extract all numbers from the path
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', d)
        if len(numbers) < 2:
            return BBox(ll=Point(0, 0), ur=Point(0, 0))

        # Pair up as x,y coordinates
        coords = []
        for i in range(0, len(numbers) - 1, 2):
            try:
                coords.append((float(numbers[i]), float(numbers[i + 1])))
            except (ValueError, IndexError):
                pass

        if not coords:
            return BBox(ll=Point(0, 0), ur=Point(0, 0))

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]

        return BBox(
            ll=Point(min(xs), max(ys)),
            ur=Point(max(xs), min(ys)),
        )

    @property
    def x(self) -> float:
        return self._bbox.ll.x

    @property
    def y(self) -> float:
        return self._bbox.ur.y

    @property
    def width(self) -> float:
        return self._bbox.ur.x - self._bbox.ll.x

    @property
    def height(self) -> float:
        return self._bbox.ll.y - self._bbox.ur.y

    @property
    def bbox(self) -> BBox:
        return self._bbox

    @property
    def points(self) -> Points:
        return Points(self)

    def svg_path(self) -> str:
        return self.d
