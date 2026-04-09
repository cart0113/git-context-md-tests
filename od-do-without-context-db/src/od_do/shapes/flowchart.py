"""
Flowchart and diagram shapes for OD-DO.

Provides common shapes used in flowcharts, architecture diagrams, and technical drawings:
- Diamond (decision)
- Parallelogram (data/IO)
- Document (document shape with wavy bottom)
- Cylinder (database)
- Cloud (cloud services, thoughts)

Example:
    from od_do.shapes import flowchart
    from od_do import colors

    # Decision diamond
    diamond = flowchart.Diamond(
        parent=diagram,
        center=(200, 200),
        width=100,
        height=60,
        fill=colors.LIGHT_YELLOW,
        stroke=colors.BLACK,
    )

    # Data parallelogram
    para = flowchart.Parallelogram(
        parent=diagram,
        ll=(100, 300),
        width=120,
        height=60,
        fill=colors.LIGHT_BLUE,
    )

    # Database cylinder
    db = flowchart.Cylinder(
        parent=diagram,
        center=(300, 200),
        width=80,
        height=100,
        fill=colors.LIGHT_GRAY,
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


class Diamond:
    """A diamond/rhombus shape for decisions in flowcharts.

    Defined by center point, width, and height.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        width: float,
        height: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.center = Point.resolve_point(center)
        self._width = width
        self._height = height
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def vertices(self) -> List[Point]:
        cx, cy = self.center.x, self.center.y
        hw, hh = self._width / 2, self._height / 2
        return [
            Point(cx, cy - hh),
            Point(cx + hw, cy),
            Point(cx, cy + hh),
            Point(cx - hw, cy),
        ]

    @property
    def x(self) -> float:
        return self.center.x - self._width / 2

    @property
    def y(self) -> float:
        return self.center.y - self._height / 2

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def bbox(self) -> BBox:
        hw, hh = self._width / 2, self._height / 2
        return BBox(
            ll=Point(self.center.x - hw, self.center.y + hh),
            ur=Point(self.center.x + hw, self.center.y - hh),
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


class Parallelogram:
    """A parallelogram shape for data/IO in flowcharts.

    Defined by lower-left corner, width, height, and slant.
    The slant determines how much the top edge is offset from the bottom.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        width: float,
        height: float,
        slant: Optional[float] = None,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self._ll = Point.resolve_point(ll)
        self._width = width
        self._height = height
        self.slant = slant if slant is not None else width * 0.2
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def vertices(self) -> List[Point]:
        x, y = self._ll.x, self._ll.y
        return [
            Point(x, y),
            Point(x + self._width, y),
            Point(x + self._width + self.slant, y - self._height),
            Point(x + self.slant, y - self._height),
        ]

    @property
    def x(self) -> float:
        return self._ll.x

    @property
    def y(self) -> float:
        return self._ll.y - self._height

    @property
    def width(self) -> float:
        return self._width + self.slant

    @property
    def height(self) -> float:
        return self._height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y),
            ur=Point(self._ll.x + self._width + self.slant, self._ll.y - self._height),
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


class Document:
    """A document shape with wavy bottom edge.

    Common in flowcharts to represent documents or reports.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        width: float,
        height: float,
        wave_height: Optional[float] = None,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self._ll = Point.resolve_point(ll)
        self._width = width
        self._height = height
        self.wave_height = wave_height if wave_height is not None else height * 0.1
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

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
        return self._height + self.wave_height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y + self.wave_height),
            ur=Point(self._ll.x + self._width, self._ll.y - self._height),
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

    def svg_path(self) -> str:
        x, y = self._ll.x, self._ll.y
        w, h = self._width, self._height
        wh = self.wave_height
        return (
            f"M {x},{y} "
            f"L {x},{y - h} "
            f"L {x + w},{y - h} "
            f"L {x + w},{y} "
            f"Q {x + w * 0.75},{y + wh} {x + w * 0.5},{y} "
            f"Q {x + w * 0.25},{y - wh} {x},{y} Z"
        )


class Cylinder:
    """A 3D cylinder shape for databases.

    Defined by center, width (diameter), and height.
    The ellipse_ratio controls the height of the top/bottom ellipses.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        width: float,
        height: float,
        ellipse_ratio: float = 0.2,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.center = Point.resolve_point(center)
        self._width = width
        self._height = height
        self.ellipse_ratio = ellipse_ratio
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def ellipse_height(self) -> float:
        return self._width * self.ellipse_ratio

    @property
    def x(self) -> float:
        return self.center.x - self._width / 2

    @property
    def y(self) -> float:
        return self.center.y - self._height / 2 - self.ellipse_height / 2

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height + self.ellipse_height

    @property
    def bbox(self) -> BBox:
        hw, hh = self._width / 2, self._height / 2
        eh = self.ellipse_height / 2
        return BBox(
            ll=Point(self.center.x - hw, self.center.y + hh + eh),
            ur=Point(self.center.x + hw, self.center.y - hh - eh),
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

    @property
    def top_y(self) -> float:
        return self.center.y - self._height / 2

    @property
    def bottom_y(self) -> float:
        return self.center.y + self._height / 2

    def svg_body_path(self) -> str:
        rx = self._width / 2
        ry = self.ellipse_height / 2
        cx = self.center.x
        top_y = self.top_y
        bottom_y = self.bottom_y
        return (
            f"M {cx - rx},{top_y} "
            f"L {cx - rx},{bottom_y} "
            f"A {rx},{ry} 0 0,0 {cx + rx},{bottom_y} "
            f"L {cx + rx},{top_y} "
            f"A {rx},{ry} 0 0,1 {cx - rx},{top_y} Z"
        )

    def svg_top_path(self) -> str:
        rx = self._width / 2
        ry = self.ellipse_height / 2
        cx = self.center.x
        top_y = self.top_y
        return f"M {cx - rx},{top_y} A {rx},{ry} 0 1,1 {cx + rx},{top_y} A {rx},{ry} 0 1,1 {cx - rx},{top_y} Z"


class Cloud:
    """A cloud shape for cloud services or thoughts.

    Creates a cloud-like blob using overlapping circles.
    """

    def __init__(
        self,
        parent: "Diagram",
        center: PointLike,
        width: float,
        height: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self.center = Point.resolve_point(center)
        self._width = width
        self._height = height
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

    @property
    def x(self) -> float:
        return self.center.x - self._width / 2

    @property
    def y(self) -> float:
        return self.center.y - self._height / 2

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def bbox(self) -> BBox:
        hw, hh = self._width / 2, self._height / 2
        return BBox(
            ll=Point(self.center.x - hw, self.center.y + hh),
            ur=Point(self.center.x + hw, self.center.y - hh),
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

    def svg_path(self) -> str:
        cx, cy = self.center.x, self.center.y
        w, h = self._width, self._height
        return (
            f"M {cx - w * 0.35},{cy + h * 0.15} "
            f"a {w * 0.2},{h * 0.25} 0 1,1 {w * 0.1},{-h * 0.35} "
            f"a {w * 0.25},{h * 0.3} 0 1,1 {w * 0.35},{-h * 0.1} "
            f"a {w * 0.2},{h * 0.25} 0 1,1 {w * 0.25},{h * 0.15} "
            f"a {w * 0.15},{h * 0.2} 0 1,1 {-w * 0.05},{h * 0.3} "
            f"a {w * 0.2},{h * 0.15} 0 1,1 {-w * 0.3},{h * 0.1} "
            f"a {w * 0.25},{h * 0.2} 0 1,1 {-w * 0.35},{-h * 0.1} Z"
        )


class Terminator:
    """A terminator/stadium shape for start/end in flowcharts.

    A rectangle with fully rounded ends (pill shape).
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        width: float,
        height: float,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
    ):
        self._ll = Point.resolve_point(ll)
        self._width = width
        self._height = height
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else None
        self.stroke_width = stroke_width
        self.parent = parent
        parent.add_shape(self)

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

    def svg_path(self) -> str:
        x, y = self._ll.x, self._ll.y
        w, h = self._width, self._height
        r = h / 2
        return (
            f"M {x + r},{y} "
            f"L {x + w - r},{y} "
            f"A {r},{r} 0 0,1 {x + w - r},{y - h} "
            f"L {x + r},{y - h} "
            f"A {r},{r} 0 0,1 {x + r},{y} Z"
        )
