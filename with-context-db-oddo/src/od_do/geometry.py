"""
Geometry primitives for OD-DO diagrams.

Provides Point, BBox, and Points classes for coordinate handling
and shape anchor point access.

Example:
    from od_do.geometry import Point, BBox

    # Create points
    p1 = Point(100, 200)
    p2 = Point(300, 400)

    # Point arithmetic
    p3 = p1 + p2           # Point(400, 600)
    p4 = p1 + (50, 50)     # Point(150, 250)

    # Create bounding box
    bbox = BBox(ll=p1, ur=p2)
    print(bbox.width)      # 200
    print(bbox.height)     # 200
"""

from __future__ import annotations

from typing import Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .shapes.base import Shape

PointLike = Union["Point", Tuple[float, float]]


def resolve_position(
    width: float,
    height: float,
    ll: Optional[PointLike] = None,
    ul: Optional[PointLike] = None,
    lr: Optional[PointLike] = None,
    ur: Optional[PointLike] = None,
) -> Tuple[float, float]:
    """Convert corner position to (x, y) upper-left coordinates.

    In SVG coordinates, Y increases downward, so:
    - ul (upper-left) has the smallest y value
    - ll (lower-left) = ul + (0, height)
    - ur (upper-right) = ul + (width, 0)
    - lr (lower-right) = ul + (width, height)

    Args:
        width: Width of the shape/diagram.
        height: Height of the shape/diagram.
        ll: Lower-left corner position (Point or 2-tuple).
        ul: Upper-left corner position (Point or 2-tuple).
        lr: Lower-right corner position (Point or 2-tuple).
        ur: Upper-right corner position (Point or 2-tuple).

    Returns:
        Tuple of (x, y) for the upper-left corner.

    Raises:
        ValueError: If more than one position is specified.
    """

    def to_tuple(p: PointLike) -> Tuple[float, float]:
        if isinstance(p, Point):
            return (p.x, p.y)
        return p

    specified = sum([ll is not None, ul is not None, lr is not None, ur is not None])

    if specified > 1:
        raise ValueError("Cannot specify multiple positioning modes (ll, ul, lr, ur)")

    if specified == 0:
        ll = (0, 0)

    if ll is not None:
        px, py = to_tuple(ll)
        return (px, py - height)

    if ul is not None:
        px, py = to_tuple(ul)
        return (px, py)

    if lr is not None:
        px, py = to_tuple(lr)
        return (px - width, py - height)

    if ur is not None:
        px, py = to_tuple(ur)
        return (px - width, py)

    return (0, 0)


class Point:
    """A 2D point with x, y coordinates.

    Supports arithmetic operations for convenient coordinate manipulation.

    Attributes:
        x: X coordinate
        y: Y coordinate

    Example:
        p1 = Point(100, 200)
        p2 = Point(50, 50)

        p3 = p1 + p2           # Point(150, 250)
        p4 = p1 - p2           # Point(50, 150)
        p5 = p1 * 2            # Point(200, 400)
        p6 = p1 / 2            # Point(50, 100)

        # Can also add/subtract tuples
        p7 = p1 + (10, 20)     # Point(110, 220)
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        """Create a Point with x, y coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def __add__(self, other: Union[Point, Tuple[float, float]]) -> Point:
        """Add another point or tuple to this point."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])
        return NotImplemented

    def __radd__(self, other: Union[Point, Tuple[float, float]]) -> Point:
        """Support tuple + Point."""
        return self.__add__(other)

    def __sub__(self, other: Union[Point, Tuple[float, float]]) -> Point:
        """Subtract another point or tuple from this point."""
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1])
        return NotImplemented

    def __mul__(self, scalar: float) -> Point:
        """Multiply point by a scalar."""
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Point:
        """Support scalar * Point."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Point:
        """Divide point by a scalar."""
        return Point(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Point:
        """Negate the point."""
        return Point(-self.x, -self.y)

    def __iter__(self):
        """Allow unpacking: x, y = point."""
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> float:
        """Allow indexing: point[0], point[1]."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError(f"Point index out of range: {index}")

    def __len__(self) -> int:
        """Return 2 for tuple compatibility."""
        return 2

    def __eq__(self, other: object) -> bool:
        """Check equality with another Point or tuple."""
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return NotImplemented

    def __hash__(self) -> int:
        """Return hash for use in sets/dicts."""
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Point({self.x}, {self.y})"

    def __str__(self) -> str:
        """Return string representation."""
        return f"({self.x}, {self.y})"

    def as_tuple(self) -> Tuple[float, float]:
        """Return as a tuple (x, y)."""
        return (self.x, self.y)

    def distance_to(self, other: Union[Point, Tuple[float, float]]) -> float:
        """Calculate Euclidean distance to another point."""
        if isinstance(other, tuple):
            other = Point(other[0], other[1])
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def lerp(self, other: Point, t: float) -> Point:
        """Linear interpolation between this point and another.

        Args:
            other: Target point
            t: Interpolation factor (0.0 = this point, 1.0 = other point)

        Returns:
            Interpolated point
        """
        return Point(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    @classmethod
    def resolve_point(cls, point: Union[Point, Tuple[float, float]]) -> Point:
        """Resolve a Point or 2-tuple to a Point object.

        Args:
            point: A Point object or a 2-tuple of (x, y) coordinates.

        Returns:
            The same Point if already a Point, otherwise a new Point from the tuple.
        """
        if isinstance(point, cls):
            return point
        return cls(point[0], point[1])


class BBox:
    """A bounding box defined by lower-left and upper-right corners.

    In SVG/screen coordinates, Y increases downward:
    - ll (lower-left) has smaller x, larger y
    - ur (upper-right) has larger x, smaller y

    Attributes:
        ll: Lower-left corner point
        ur: Upper-right corner point

    Example:
        bbox = BBox(ll=Point(0, 100), ur=Point(200, 0))
        print(bbox.width)   # 200
        print(bbox.height)  # 100
    """

    __slots__ = ("ll", "ur")

    def __init__(self, ll: Point, ur: Point):
        """Create a BBox from lower-left and upper-right corners.

        Args:
            ll: Lower-left corner point
            ur: Upper-right corner point
        """
        self.ll = ll
        self.ur = ur

    @property
    def ul(self) -> Point:
        """Upper-left corner."""
        return Point(self.ll.x, self.ur.y)

    @property
    def lr(self) -> Point:
        """Lower-right corner."""
        return Point(self.ur.x, self.ll.y)

    @property
    def width(self) -> float:
        """Width of the bounding box."""
        return abs(self.ur.x - self.ll.x)

    @property
    def height(self) -> float:
        """Height of the bounding box."""
        return abs(self.ll.y - self.ur.y)

    @property
    def center(self) -> Point:
        """Center point of the bounding box."""
        return Point(
            (self.ll.x + self.ur.x) / 2,
            (self.ll.y + self.ur.y) / 2,
        )

    def __iter__(self):
        """Allow unpacking: ll, ur = bbox."""
        yield self.ll
        yield self.ur

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"BBox(ll={self.ll}, ur={self.ur})"

    def contains(self, point: Point) -> bool:
        """Check if a point is inside this bounding box."""
        min_x = min(self.ll.x, self.ur.x)
        max_x = max(self.ll.x, self.ur.x)
        min_y = min(self.ll.y, self.ur.y)
        max_y = max(self.ll.y, self.ur.y)
        return min_x <= point.x <= max_x and min_y <= point.y <= max_y


class Points:
    """Helper class for accessing shape anchor points.

    Provides access to corner points (ll, ul, lr, ur) and edge interpolation
    (left, right, top, bottom) for any shape.

    Corner naming convention (SVG coordinates where Y increases downward):
        ul (upper-left) ----- ur (upper-right)
              |                     |
              |                     |
        ll (lower-left) ----- lr (lower-right)

    Edge methods take a float from 0.0 to 1.0:
        - left(0.0) = ll, left(1.0) = ul
        - right(0.0) = lr, right(1.0) = ur
        - top(0.0) = ul, top(1.0) = ur
        - bottom(0.0) = ll, bottom(1.0) = lr

    Example:
        block = shapes.block(parent=diagram, ll=(100, 200), width=50, height=30)

        # Access corners
        lower_left = block.points.ll    # Point(100, 200)
        upper_right = block.points.ur   # Point(150, 170)

        # Interpolate along edges
        mid_left = block.points.left(0.5)   # Midpoint of left edge
        mid_top = block.points.top(0.5)     # Midpoint of top edge
    """

    __slots__ = ("_shape",)

    def __init__(self, shape: "Shape"):
        """Create a Points helper for a shape.

        Args:
            shape: The shape to provide anchor points for.
        """
        self._shape = shape

    @property
    def ll(self) -> Point:
        """Lower-left corner (smallest x, largest y)."""
        return Point(self._shape.x, self._shape.y + self._shape.height)

    @property
    def ul(self) -> Point:
        """Upper-left corner (smallest x, smallest y)."""
        return Point(self._shape.x, self._shape.y)

    @property
    def lr(self) -> Point:
        """Lower-right corner (largest x, largest y)."""
        return Point(self._shape.x + self._shape.width, self._shape.y + self._shape.height)

    @property
    def ur(self) -> Point:
        """Upper-right corner (largest x, smallest y)."""
        return Point(self._shape.x + self._shape.width, self._shape.y)

    @property
    def center(self) -> Point:
        """Center point of the shape."""
        return Point(
            self._shape.x + self._shape.width / 2,
            self._shape.y + self._shape.height / 2,
        )

    def left(self, t: float = 0.0) -> Point:
        """Point along the left edge.

        Args:
            t: Position from 0.0 (bottom/ll) to 1.0 (top/ul)

        Returns:
            Point on the left edge.
        """
        return self.ll.lerp(self.ul, t)

    def right(self, t: float = 0.0) -> Point:
        """Point along the right edge.

        Args:
            t: Position from 0.0 (bottom/lr) to 1.0 (top/ur)

        Returns:
            Point on the right edge.
        """
        return self.lr.lerp(self.ur, t)

    def top(self, t: float = 0.0) -> Point:
        """Point along the top edge.

        Args:
            t: Position from 0.0 (left/ul) to 1.0 (right/ur)

        Returns:
            Point on the top edge.
        """
        return self.ul.lerp(self.ur, t)

    def bottom(self, t: float = 0.0) -> Point:
        """Point along the bottom edge.

        Args:
            t: Position from 0.0 (left/ll) to 1.0 (right/lr)

        Returns:
            Point on the bottom edge.
        """
        return self.ll.lerp(self.lr, t)

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Points(ll={self.ll}, ur={self.ur})"
