"""
Path primitives for OD-DO diagrams.

Provides path drawing capabilities including lines with direction string support.

All points in a path are RELATIVE to start_point:
- Coordinate tuples like (50, 30) mean "50 units right, 30 units down from start_point"
- Direction strings like "D20", "R30" mean relative movement from the previous point

Direction strings:
- "U20" or "u20": Up 20 units (relative to previous point)
- "D20" or "d20": Down 20 units
- "L20" or "l20": Left 20 units
- "R20" or "r20": Right 20 units
- "D10:R10": Combined diagonal movement (down 10 AND right 10)

Combined directions use colon separator to move in two directions at once.
Valid combinations: U:L, U:R, D:L, D:R (and reverse order like L:U, R:U, etc.)

Example:
    from od_do.paths import Line
    from od_do import colors

    # Line with relative coordinates (relative to start_point)
    path1 = Line(
        parent=diagram,
        start_point=(100, 100),
        points=[(50, 0), (50, 50), (0, 50)],  # Offsets from start_point
        width=2,
        color=colors.DARK_BLUE,
    )

    # Line with direction strings
    path2 = Line(
        parent=diagram,
        start_point=block.points.ll,
        points=["D20", "R30", "U10"],
        width=2,
        color=colors.RED,
    )

    # Mixed relative coordinates and direction strings
    path3 = Line(
        parent=diagram,
        start_point=(50, 50),
        points=[(50, 0), "D20", "R20"],  # (50,0) is relative to start
        width=2,
        color=colors.GREEN,
    )

    # Using combined directions for diagonal movement
    path4 = Line(
        parent=diagram,
        start_point=block.points.lr,
        points=["R100", "D100", "R100", "D10:R10"],  # Last point is diagonal
        width=2,
        color=colors.DARK_GRAY,
    )
"""

from __future__ import annotations

import re
from typing import List, Optional, Union, Tuple, TYPE_CHECKING

from .geometry import Point, BBox, Points
from .colors import Color
from .markers import Marker, resolve_line_style, LineStyleType

if TYPE_CHECKING:
    from .diagram.base import Diagram


PointLike = Union[Point, Tuple[float, float]]
PathPoint = Union[PointLike, str]


SINGLE_DIRECTION_PATTERN = re.compile(r"^([UDLRudlr])(\d+(?:\.\d+)?)$")
COMBINED_DIRECTION_PATTERN = re.compile(
    r"^([UDLRudlr])(\d+(?:\.\d+)?):([UDLRudlr])(\d+(?:\.\d+)?)$"
)


def validate_point(point: PathPoint, index: int) -> None:
    """Validate a single path point and raise a clear error if invalid.

    Args:
        point: The point to validate (can be tuple, Point, or string).
        index: The index of this point in the points list (for error messages).

    Raises:
        ValueError: If the point format is invalid, with a detailed error message.
    """
    if isinstance(point, str):
        point = point.strip()

        if SINGLE_DIRECTION_PATTERN.match(point):
            return

        if COMBINED_DIRECTION_PATTERN.match(point):
            match = COMBINED_DIRECTION_PATTERN.match(point)
            dir1 = match.group(1).upper()
            dir2 = match.group(3).upper()

            vertical = {"U", "D"}
            horizontal = {"L", "R"}

            if dir1 in vertical and dir2 in vertical:
                raise ValueError(
                    f"Invalid combined direction at index {index}: {point!r}. "
                    f"Cannot combine two vertical directions (U/D). "
                    f"Use one vertical and one horizontal, e.g., 'D10:R10'."
                )
            if dir1 in horizontal and dir2 in horizontal:
                raise ValueError(
                    f"Invalid combined direction at index {index}: {point!r}. "
                    f"Cannot combine two horizontal directions (L/R). "
                    f"Use one vertical and one horizontal, e.g., 'D10:R10'."
                )
            return

        if ":" in point:
            raise ValueError(
                f"Invalid combined direction at index {index}: {point!r}. "
                f"Expected format like 'D10:R10' (direction + number : direction + number). "
                f"Valid directions: U (up), D (down), L (left), R (right)."
            )

        raise ValueError(
            f"Invalid direction string at index {index}: {point!r}. "
            f"Expected single direction like 'U20', 'D10', 'L5', 'R30' "
            f"or combined diagonal like 'D10:R10'. "
            f"Valid directions: U (up), D (down), L (left), R (right)."
        )

    elif isinstance(point, tuple):
        if len(point) != 2:
            raise ValueError(
                f"Invalid coordinate tuple at index {index}: {point!r}. "
                f"Expected a 2-tuple like (x, y), got {len(point)} elements."
            )
        if not all(isinstance(v, (int, float)) for v in point):
            raise ValueError(
                f"Invalid coordinate tuple at index {index}: {point!r}. "
                f"Both x and y must be numbers."
            )

    elif not isinstance(point, Point):
        raise ValueError(
            f"Invalid point at index {index}: {point!r} (type: {type(point).__name__}). "
            f"Expected a tuple (x, y), Point object, or direction string."
        )


def validate_points(points: List[PathPoint]) -> None:
    """Validate all points in a path and raise clear errors if invalid.

    Args:
        points: List of points to validate.

    Raises:
        ValueError: If any point is invalid, with a detailed error message.
    """
    for i, point in enumerate(points):
        validate_point(point, i)


def _parse_single_direction(dir_char: str, distance: float) -> Tuple[float, float]:
    """Convert a single direction character and distance to (dx, dy)."""
    if dir_char == "U":
        return (0, -distance)
    elif dir_char == "D":
        return (0, distance)
    elif dir_char == "L":
        return (-distance, 0)
    elif dir_char == "R":
        return (distance, 0)
    else:
        raise ValueError(f"Unknown direction: {dir_char}")


def _parse_direction(direction: str) -> Tuple[float, float]:
    """Parse a direction string into a relative (dx, dy) offset.

    Args:
        direction: Direction string like "U20", "D10", "L5", "R30"
            or combined direction like "D10:R10" for diagonal movement.

    Returns:
        Tuple of (dx, dy) relative offset.

    Raises:
        ValueError: If the direction string is invalid.
    """
    direction = direction.strip()

    combined_match = COMBINED_DIRECTION_PATTERN.match(direction)
    if combined_match:
        dir1 = combined_match.group(1).upper()
        dist1 = float(combined_match.group(2))
        dir2 = combined_match.group(3).upper()
        dist2 = float(combined_match.group(4))

        dx1, dy1 = _parse_single_direction(dir1, dist1)
        dx2, dy2 = _parse_single_direction(dir2, dist2)

        return (dx1 + dx2, dy1 + dy2)

    single_match = SINGLE_DIRECTION_PATTERN.match(direction)
    if single_match:
        dir_char = single_match.group(1).upper()
        distance = float(single_match.group(2))
        return _parse_single_direction(dir_char, distance)

    raise ValueError(
        f"Invalid direction string: {direction!r}. "
        f"Expected format: U20, D10, L5, R30 or combined like D10:R10"
    )


def _resolve_path_points(start_point: Point, points: List[PathPoint]) -> List[Point]:
    """Resolve a list of path points to absolute Points.

    All points are relative to start_point:
    - Coordinate tuples (x, y) are offsets from start_point
    - Direction strings are relative to the previous point
    - Combined directions like "D10:R10" for diagonal movement

    Args:
        start_point: The starting point (absolute position).
        points: List of points, which can be:
            - Point objects: offset from start_point
            - (x, y) tuples: offset from start_point
            - Direction strings like "U20", "D10": relative to previous point
            - Combined directions like "D10:R10": diagonal from previous point

    Returns:
        List of absolute Point objects.

    Raises:
        ValueError: If any point has an invalid format.
    """
    validate_points(points)

    result = []
    current = start_point

    for p in points:
        if isinstance(p, str):
            # Direction string - relative to current position
            dx, dy = _parse_direction(p)
            current = Point(current.x + dx, current.y + dy)
        else:
            # Coordinate tuple/Point - offset from start_point
            offset = Point.resolve_point(p)
            current = Point(start_point.x + offset.x, start_point.y + offset.y)
        result.append(current)

    return result


class Path:
    """Base class for path shapes.

    Paths are connected sequences of points that form lines or curves.
    All points are relative to start_point.
    Every path has a bounding box and points accessor.

    Attributes:
        parent: The diagram containing this path.
        start_point: Starting point of the path (absolute position).
        resolved_points: List of absolute points along the path.
        width: Stroke width of the path.
        color: Color of the path stroke.
        start_marker: Optional marker at the start of the path.
        end_marker: Optional marker at the end of the path.
        line_style: Line style - "solid", "dashed", "dotted", etc.
    """

    def __init__(
        self,
        parent: "Diagram",
        start_point: PointLike,
        points: List[PathPoint],
        width: float,
        color: Optional[Union[str, Color]],
        start_marker: Optional[Marker] = None,
        end_marker: Optional[Marker] = None,
        line_style: LineStyleType = None,
    ):
        """Create a path.

        Args:
            parent: The diagram to add this path to.
            start_point: Starting point of the path (absolute position).
            points: List of points (relative coords or direction strings).
            width: Stroke width.
            color: Stroke color.
            start_marker: Marker to draw at the start of the path.
            end_marker: Marker to draw at the end of the path.
            line_style: Line style - "solid", "dashed", "dotted", "dash_dot",
                or a tuple like (8, 4) for custom dash patterns.
        """
        self.parent = parent
        self.start_point = Point.resolve_point(start_point)
        self.width = width
        self.color = color
        self.start_marker = start_marker
        self.end_marker = end_marker
        self.line_style = line_style
        self.resolved_points = _resolve_path_points(self.start_point, points)
        parent.add_shape(self)

    @property
    def all_points(self) -> List[Point]:
        """All points including start_point."""
        return [self.start_point] + self.resolved_points

    @property
    def bbox(self) -> BBox:
        """Return the bounding box of this path, including stroke width and markers."""
        all_pts = self.all_points
        if not all_pts:
            return BBox(ll=Point(0, 0), ur=Point(0, 0))

        min_x = min(p.x for p in all_pts)
        max_x = max(p.x for p in all_pts)
        min_y = min(p.y for p in all_pts)
        max_y = max(p.y for p in all_pts)

        half_width = self.width / 2
        min_x -= half_width
        max_x += half_width
        min_y -= half_width
        max_y += half_width

        if self.end_marker and len(all_pts) >= 2:
            end_pt = all_pts[-1]
            prev_pt = all_pts[-2]
            marker_extent = self._calculate_marker_extent(self.end_marker, prev_pt, end_pt)
            min_x = min(min_x, marker_extent[0])
            max_x = max(max_x, marker_extent[1])
            min_y = min(min_y, marker_extent[2])
            max_y = max(max_y, marker_extent[3])

        if self.start_marker and len(all_pts) >= 2:
            start_pt = all_pts[0]
            next_pt = all_pts[1]
            marker_extent = self._calculate_marker_extent(self.start_marker, next_pt, start_pt)
            min_x = min(min_x, marker_extent[0])
            max_x = max(max_x, marker_extent[1])
            min_y = min(min_y, marker_extent[2])
            max_y = max(max_y, marker_extent[3])

        return BBox(
            ll=Point(min_x, max_y),
            ur=Point(max_x, min_y),
        )

    def _calculate_marker_extent(
        self,
        marker: Marker,
        from_pt: Point,
        to_pt: Point,
    ) -> Tuple[float, float, float, float]:
        """Calculate the bounding extent (min_x, max_x, min_y, max_y) of a marker.

        The marker points in the direction from from_pt to to_pt, placed at to_pt.
        """
        import math

        size = marker.get_size(self.width)
        length = marker.get_length()

        h = size * 0.6
        w = h * length

        dx = to_pt.x - from_pt.x
        dy = to_pt.y - from_pt.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.0001:
            return (to_pt.x - w, to_pt.x + w, to_pt.y - h / 2, to_pt.y + h / 2)

        dir_x = dx / dist
        dir_y = dy / dist

        tip_x = to_pt.x + dir_x * w
        tip_y = to_pt.y + dir_y * w

        perp_x = -dir_y
        perp_y = dir_x
        base1_x = to_pt.x + perp_x * h / 2
        base1_y = to_pt.y + perp_y * h / 2
        base2_x = to_pt.x - perp_x * h / 2
        base2_y = to_pt.y - perp_y * h / 2

        xs = [tip_x, base1_x, base2_x]
        ys = [tip_y, base1_y, base2_y]

        return (min(xs), max(xs), min(ys), max(ys))

    @property
    def x(self) -> float:
        """X coordinate of upper-left of bounding box (for Shape compatibility)."""
        return self.bbox.ur.x - (self.bbox.ur.x - self.bbox.ll.x)

    @property
    def y(self) -> float:
        """Y coordinate of upper-left of bounding box (for Shape compatibility)."""
        return self.bbox.ur.y

    @property
    def height(self) -> float:
        """Height of bounding box (for Shape compatibility)."""
        return self.bbox.height

    @property
    def points_helper(self) -> Points:
        """Return anchor points helper for this path's bounding box."""
        return Points(self)

    @property
    def ll(self) -> Point:
        """Lower-left corner of bounding box."""
        return self.bbox.ll

    @property
    def ur(self) -> Point:
        """Upper-right corner of bounding box."""
        return self.bbox.ur

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y) for this path.

        For backward compatibility with Shape interface.
        """
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    @property
    def stroke_color(self) -> Optional[str]:
        """Return stroke color as a string suitable for SVG."""
        if self.color is None:
            return None
        if isinstance(self.color, Color):
            return self.color.svg_color()
        return self.color

    @property
    def stroke_opacity(self) -> Optional[float]:
        """Return stroke opacity if color is a Color with alpha < 1."""
        if isinstance(self.color, Color) and self.color.a < 1.0:
            return self.color.a
        return None

    @property
    def dash_pattern(self) -> Optional[Tuple[float, ...]]:
        """Return the dash pattern tuple for this path's line style."""
        return resolve_line_style(self.line_style)


class Line(Path):
    """A polyline path connecting multiple points.

    Lines are paths with no fill, only a stroke connecting the points.

    Example:
        line = Line(
            parent=diagram,
            start_point=(100, 100),
            points=[(50, 0), (50, 50)],  # Relative to start_point
            width=2,
            color=colors.BLUE,
        )
    """

    pass


class StrokeLine(Line):
    """A polyline with stroked edges on the top and bottom, but not the ends.

    This line type renders as a filled line with stroke outlines on the
    parallel edges. Markers are not supported on this line type.

    The width must be >= 2 * stroke_width to ensure the fill area is visible.

    Example:
        line = StrokeLine(
            parent=diagram,
            start_point=(100, 100),
            points=["D20", "R30"],
            width=10,
            color=colors.DARK_RED,
            stroke_color=colors.RED,
        )
    """

    def __init__(
        self,
        parent: "Diagram",
        start_point: PointLike,
        points: List[PathPoint],
        width: float,
        color: Optional[Union[str, Color]],
        stroke_color: Optional[Union[str, Color]],
        stroke_width: float = 1,
        line_style: LineStyleType = None,
    ):
        if width < 2 * stroke_width:
            raise ValueError(
                f"StrokeLine width ({width}) must be >= 2 * stroke_width ({2 * stroke_width})"
            )
        self.edge_stroke_color = stroke_color
        self.edge_stroke_width = stroke_width
        super().__init__(
            parent=parent,
            start_point=start_point,
            points=points,
            width=width,
            color=color,
            start_marker=None,
            end_marker=None,
            line_style=line_style,
        )
