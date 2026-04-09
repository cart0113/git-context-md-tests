"""
Marker definitions for line endpoints.

Markers are decorative elements placed at the start or end of lines,
such as arrows, circles, squares, and diamonds.

Example:
    from od_do import Line, Arrow, Circle
    from od_do import colors

    # Line with arrow at end (using named size)
    Line(
        parent=diagram,
        start_point=(100, 100),
        points=["R100"],
        width=2,
        color=colors.BLUE,
        end_marker=Arrow(),  # defaults to size="medium"
    )

    # Bidirectional arrow with explicit size
    Line(
        parent=diagram,
        start_point=(100, 100),
        points=["R100"],
        width=2,
        color=colors.RED,
        start_marker=Arrow(size="small"),
        end_marker=Arrow(size="large"),
    )

    # Circle endpoint with absolute size
    Line(
        parent=diagram,
        start_point=(100, 100),
        points=["R100"],
        width=2,
        end_marker=Circle(size=6, filled=True, color=colors.GREEN),
    )
"""

from __future__ import annotations

from typing import Optional, Union, Tuple

from .colors import Color


MARKER_SIZES = {
    "very_small": 2.0,
    "very-small": 2.0,
    "small": 3.0,
    "medium": 5.0,
    "large": 7.0,
    "very_large": 10.0,
    "very-large": 10.0,
}

MARKER_LENGTHS = {
    "very-short": 0.4,
    "very_short": 0.4,
    "short": 0.6,
    "medium": 1.0,
    "tall": 1.4,
    "very-tall": 2.0,
    "very_tall": 2.0,
}

MarkerSizeType = Union[float, str]
MarkerLengthType = Union[float, str]


def resolve_marker_length(length: MarkerLengthType) -> float:
    """Resolve a marker length to a multiplier.

    Args:
        length: Marker length - can be:
            - A float: Direct multiplier (1.0 = normal)
            - A string: Named length ("very-short", "short", "medium", "tall", "very-tall")

    Returns:
        Length multiplier (1.0 = normal proportions).

    Raises:
        ValueError: If the length string is not recognized.
    """
    if isinstance(length, (int, float)):
        return float(length)

    if isinstance(length, str):
        length_lower = length.lower().replace("_", "-")
        if length_lower not in MARKER_LENGTHS:
            valid = ", ".join(
                f'"{s}"' for s in ["very-short", "short", "medium", "tall", "very-tall"]
            )
            raise ValueError(
                f"Unknown marker length: {length!r}. Valid lengths: {valid}, "
                f"or provide a numeric multiplier."
            )
        return MARKER_LENGTHS[length_lower]

    raise ValueError(f"Invalid marker length type: {type(length).__name__}. Expected float or str.")


def resolve_marker_size(size: MarkerSizeType, line_width: float) -> float:
    """Resolve a marker size to an absolute value.

    Args:
        size: Marker size - can be:
            - A float: Absolute size in user units
            - A string: Named size that scales with line width
              ("very-small", "small", "medium", "large", "very-large")

    Returns:
        Absolute size in user units.

    Raises:
        ValueError: If the size string is not recognized.
    """
    if isinstance(size, (int, float)):
        return float(size)

    if isinstance(size, str):
        size_lower = size.lower().replace("_", "-")
        if size_lower not in MARKER_SIZES:
            valid = ", ".join(
                f'"{s}"' for s in ["very-small", "small", "medium", "large", "very-large"]
            )
            raise ValueError(
                f"Unknown marker size: {size!r}. Valid sizes: {valid}, "
                f"or provide a numeric value."
            )
        return MARKER_SIZES[size_lower] * line_width

    raise ValueError(f"Invalid marker size type: {type(size).__name__}. " f"Expected float or str.")


class Marker:
    """Base class for line endpoint markers.

    Markers are decorative elements placed at the start or end of lines.
    When color is None, the marker inherits the line's color.

    Attributes:
        size: Size of the marker. Can be:
            - A float for absolute size in user units
            - A string for named sizes: "very-small", "small", "medium", "large", "very-large"
              Named sizes scale with line width (medium = 5x line width)
        length: Length/pointiness of the marker. Can be:
            - A float multiplier (1.0 = normal)
            - A string: "very-short", "short", "medium", "tall", "very-tall"
        color: Marker color. If None, inherits from the line.
        filled: Whether the marker shape is filled (for applicable markers).
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        length: MarkerLengthType = "medium",
        color: Optional[Union[str, Color]] = None,
        filled: bool = True,
    ):
        self.size = size
        self.length = length
        self.color = color
        self.filled = filled

    def get_size(self, line_width: float) -> float:
        """Get the resolved size for this marker.

        Args:
            line_width: The width of the line this marker is attached to.

        Returns:
            The absolute size in user units.
        """
        return resolve_marker_size(self.size, line_width)

    def get_length(self) -> float:
        """Get the resolved length multiplier for this marker.

        Returns:
            Length multiplier (1.0 = normal proportions).
        """
        return resolve_marker_length(self.length)

    def get_color(self, line_color: Optional[Union[str, Color]]) -> Optional[Union[str, Color]]:
        """Get the effective color for this marker.

        Args:
            line_color: The color of the line this marker is attached to.

        Returns:
            The marker's color if set, otherwise the line's color.
        """
        if self.color is not None:
            return self.color
        return line_color

    def svg_id_prefix(self) -> str:
        """Return prefix for SVG marker ID."""
        return "marker"


class Arrow(Marker):
    """Arrow/arrowhead marker for line endpoints.

    Creates a triangular arrowhead pointing in the direction of the line.

    Attributes:
        size: Width of the arrow base. Default is "medium" which scales with line width.
        length: How long/pointy the arrow is. Default is "medium".
            "very-short", "short", "medium", "tall", "very-tall" or a float multiplier.
        color: Arrow color. If None, inherits from the line.
        filled: Whether the arrow is filled (True) or open outline (False).
        style: Arrow style - "closed" (default), "open", or "barbed".
        invert: If True, arrow points into the line instead of away from it.
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        length: MarkerLengthType = "medium",
        color: Optional[Union[str, Color]] = None,
        filled: bool = True,
        style: str = "closed",
        invert: bool = False,
    ):
        super().__init__(size=size, length=length, color=color, filled=filled)
        self.style = style
        self.invert = invert

    def svg_id_prefix(self) -> str:
        return "arrow"


class Circle(Marker):
    """Circle marker for line endpoints.

    Creates a circular marker at the line endpoint.

    Attributes:
        size: Diameter of the circle. Default is "medium" which scales with line width.
        color: Circle color. If None, inherits from the line.
        filled: Whether the circle is filled or just an outline.
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        color: Optional[Union[str, Color]] = None,
        filled: bool = True,
    ):
        super().__init__(size=size, color=color, filled=filled)

    def svg_id_prefix(self) -> str:
        return "circle"


class Square(Marker):
    """Square marker for line endpoints.

    Creates a square marker at the line endpoint.

    Attributes:
        size: Side length of the square. Default is "medium" which scales with line width.
            Note: Square uses half the size multiplier of other markers for better proportions.
        color: Square color. If None, inherits from the line.
        filled: Whether the square is filled or just an outline.
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        color: Optional[Union[str, Color]] = None,
        filled: bool = True,
    ):
        super().__init__(size=size, color=color, filled=filled)

    def get_size(self, line_width: float) -> float:
        return resolve_marker_size(self.size, line_width) / 2

    def svg_id_prefix(self) -> str:
        return "square"


class Diamond(Marker):
    """Diamond marker for line endpoints.

    Creates a diamond (rotated square) marker at the line endpoint.

    Attributes:
        size: Width/height of the diamond. Default is "medium" which scales with line width.
        color: Diamond color. If None, inherits from the line.
        filled: Whether the diamond is filled or just an outline.
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        color: Optional[Union[str, Color]] = None,
        filled: bool = True,
    ):
        super().__init__(size=size, color=color, filled=filled)

    def svg_id_prefix(self) -> str:
        return "diamond"


class Bar(Marker):
    """Bar (perpendicular line) marker for line endpoints.

    Creates a perpendicular line at the endpoint, commonly used
    in ER diagrams to indicate "one" relationships.

    Attributes:
        size: Length of the bar. Default is "medium" which scales with line width.
        color: Bar color. If None, inherits from the line.
    """

    def __init__(
        self,
        size: MarkerSizeType = "medium",
        color: Optional[Union[str, Color]] = None,
    ):
        super().__init__(size=size, color=color, filled=False)

    def svg_id_prefix(self) -> str:
        return "bar"


LINE_STYLES = {
    "solid": None,
    "dashed": (8, 4),
    "dotted": (2, 4),
    "dash_dot": (8, 4, 2, 4),
    "dash_dot_dot": (8, 4, 2, 4, 2, 4),
    "long_dash": (16, 6),
    "short_dash": (4, 4),
}

LineStyleType = Union[str, Tuple[float, ...], None]


def resolve_line_style(style: LineStyleType) -> Optional[Tuple[float, ...]]:
    """Resolve a line style to a dash pattern tuple.

    Args:
        style: Line style - can be:
            - None or "solid": No dashing (solid line)
            - String name: "dashed", "dotted", "dash_dot", etc.
            - Tuple: Custom dash pattern like (8, 4) or (8, 4, 2, 4)

    Returns:
        Tuple of dash/gap values, or None for solid lines.

    Raises:
        ValueError: If the style string is not recognized.
    """
    if style is None:
        return None

    if isinstance(style, tuple):
        return style

    if isinstance(style, str):
        style_lower = style.lower()
        if style_lower not in LINE_STYLES:
            valid = ", ".join(f'"{s}"' for s in LINE_STYLES.keys())
            raise ValueError(
                f"Unknown line style: {style!r}. Valid styles: {valid}, "
                f"or provide a custom tuple like (8, 4)."
            )
        return LINE_STYLES[style_lower]

    raise ValueError(
        f"Invalid line style type: {type(style).__name__}. " f"Expected str, tuple, or None."
    )
