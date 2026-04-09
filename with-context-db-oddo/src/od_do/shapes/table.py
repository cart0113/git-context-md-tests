"""
Table shapes for OD-DO.

Provides tables with headers, rows, and configurable styling.
Useful for database diagrams, data tables, and structured layouts.

Example:
    from od_do.shapes import table
    from od_do import colors

    # Simple table with header
    t = table.Table(
        parent=diagram,
        ll=(100, 300),
        columns=["Name", "Type", "Description"],
        rows=[
            ["id", "int", "Primary key"],
            ["name", "string", "User name"],
            ["email", "string", "Email address"],
        ],
        header_fill=colors.DARK_BLUE,
        header_text_color=colors.WHITE,
        fill=colors.WHITE,
        stroke=colors.BLACK,
    )

    # Entity table for ER diagrams
    e = table.EntityTable(
        parent=diagram,
        ll=(300, 300),
        title="users",
        rows=[
            ("id", "INT", "PK"),
            ("name", "VARCHAR(100)", ""),
            ("email", "VARCHAR(255)", "UK"),
        ],
        title_fill=colors.DARK_GREEN,
    )
"""

from __future__ import annotations

from typing import Optional, Union, Tuple, List, TYPE_CHECKING

from ..geometry import Point, BBox, Points
from ..colors import Color, ColorLike

if TYPE_CHECKING:
    from ..diagram.base import Diagram

PointLike = Union[Point, Tuple[float, float]]


class Table:
    """A table with optional header row and data rows.

    Columns can have fixed widths or auto-size to content.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        columns: List[str],
        rows: List[List[str]],
        column_widths: Optional[List[float]] = None,
        row_height: float = 25,
        header_height: Optional[float] = None,
        font_size: float = 12,
        font_family: str = "sans-serif",
        padding: float = 8,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        header_fill: Optional[ColorLike] = None,
        header_text_color: Optional[ColorLike] = None,
        text_color: Optional[ColorLike] = None,
        alternate_fill: Optional[ColorLike] = None,
    ):
        self._ll = Point.resolve_point(ll)
        self.columns = columns
        self.rows = rows
        self.row_height = row_height
        self.header_height = header_height if header_height is not None else row_height
        self.font_size = font_size
        self.font_family = font_family
        self.padding = padding
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else Color("#000000")
        self.stroke_width = stroke_width
        self.header_fill = Color.resolve_color(header_fill) if header_fill is not None else None
        self.header_text_color = Color.resolve_color(header_text_color) if header_text_color is not None else Color("#000000")
        self.text_color = Color.resolve_color(text_color) if text_color is not None else Color("#000000")
        self.alternate_fill = Color.resolve_color(alternate_fill) if alternate_fill is not None else None
        self.parent = parent

        if column_widths is not None:
            self.column_widths = column_widths
        else:
            self.column_widths = self._calculate_column_widths()

        parent.add_shape(self)

    def _calculate_column_widths(self) -> List[float]:
        widths = []
        for i, col in enumerate(self.columns):
            max_width = len(col) * self.font_size * 0.6 + self.padding * 2
            for row in self.rows:
                if i < len(row):
                    cell_width = len(row[i]) * self.font_size * 0.6 + self.padding * 2
                    max_width = max(max_width, cell_width)
            widths.append(max_width)
        return widths

    @property
    def total_width(self) -> float:
        return sum(self.column_widths)

    @property
    def total_height(self) -> float:
        return self.header_height + len(self.rows) * self.row_height

    @property
    def x(self) -> float:
        return self._ll.x

    @property
    def y(self) -> float:
        return self._ll.y - self.total_height

    @property
    def width(self) -> float:
        return self.total_width

    @property
    def height(self) -> float:
        return self.total_height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y),
            ur=Point(self._ll.x + self.total_width, self._ll.y - self.total_height),
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
    def header_fill_color(self) -> Optional[str]:
        if self.header_fill is None:
            return None
        if isinstance(self.header_fill, Color):
            return self.header_fill.svg_color()
        return self.header_fill

    @property
    def header_text_color_str(self) -> str:
        if isinstance(self.header_text_color, Color):
            return self.header_text_color.svg_color()
        return self.header_text_color

    @property
    def text_color_str(self) -> str:
        if isinstance(self.text_color, Color):
            return self.text_color.svg_color()
        return self.text_color

    @property
    def alternate_fill_color(self) -> Optional[str]:
        if self.alternate_fill is None:
            return None
        if isinstance(self.alternate_fill, Color):
            return self.alternate_fill.svg_color()
        return self.alternate_fill

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    def get_cell_x(self, col_index: int) -> float:
        x = self._ll.x
        for i in range(col_index):
            x += self.column_widths[i]
        return x

    def get_row_y(self, row_index: int) -> float:
        return self._ll.y - self.total_height + self.header_height + row_index * self.row_height


class EntityTable:
    """A table specifically for ER diagrams with a title row and attribute rows.

    Each row can have a key indicator (PK, FK, UK) shown with an icon or symbol.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        title: str,
        rows: List[Tuple[str, str, str]],
        column_widths: Optional[List[float]] = None,
        row_height: float = 22,
        title_height: Optional[float] = None,
        font_size: float = 11,
        font_family: str = "monospace",
        padding: float = 6,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        title_fill: Optional[ColorLike] = None,
        title_text_color: Optional[ColorLike] = None,
        text_color: Optional[ColorLike] = None,
    ):
        self._ll = Point.resolve_point(ll)
        self.title = title
        self.rows = rows
        self.row_height = row_height
        self.title_height = title_height if title_height is not None else row_height + 4
        self.font_size = font_size
        self.font_family = font_family
        self.padding = padding
        self.fill = Color.resolve_color(fill) if fill is not None else Color("#FFFFFF")
        self.stroke = Color.resolve_color(stroke) if stroke is not None else Color("#000000")
        self.stroke_width = stroke_width
        self.title_fill = Color.resolve_color(title_fill) if title_fill is not None else Color("#4A90D9")
        self.title_text_color = Color.resolve_color(title_text_color) if title_text_color is not None else Color("#FFFFFF")
        self.text_color = Color.resolve_color(text_color) if text_color is not None else Color("#000000")
        self.parent = parent

        if column_widths is not None:
            self.column_widths = column_widths
        else:
            self.column_widths = self._calculate_column_widths()

        parent.add_shape(self)

    def _calculate_column_widths(self) -> List[float]:
        name_width = len(self.title) * self.font_size * 0.6 + self.padding * 2
        type_width = self.padding * 2
        key_width = 30

        for name, dtype, key in self.rows:
            name_w = len(name) * self.font_size * 0.6 + self.padding * 2
            type_w = len(dtype) * self.font_size * 0.6 + self.padding * 2
            name_width = max(name_width, name_w)
            type_width = max(type_width, type_w)

        return [name_width, type_width, key_width]

    @property
    def total_width(self) -> float:
        return sum(self.column_widths)

    @property
    def total_height(self) -> float:
        return self.title_height + len(self.rows) * self.row_height

    @property
    def x(self) -> float:
        return self._ll.x

    @property
    def y(self) -> float:
        return self._ll.y - self.total_height

    @property
    def width(self) -> float:
        return self.total_width

    @property
    def height(self) -> float:
        return self.total_height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y),
            ur=Point(self._ll.x + self.total_width, self._ll.y - self.total_height),
        )

    @property
    def points(self) -> Points:
        return Points(self)

    @property
    def fill_color(self) -> Optional[str]:
        if isinstance(self.fill, Color):
            return self.fill.svg_color()
        return self.fill

    @property
    def stroke_color(self) -> Optional[str]:
        if isinstance(self.stroke, Color):
            return self.stroke.svg_color()
        return self.stroke

    @property
    def title_fill_color(self) -> str:
        if isinstance(self.title_fill, Color):
            return self.title_fill.svg_color()
        return self.title_fill

    @property
    def title_text_color_str(self) -> str:
        if isinstance(self.title_text_color, Color):
            return self.title_text_color.svg_color()
        return self.title_text_color

    @property
    def text_color_str(self) -> str:
        if isinstance(self.text_color, Color):
            return self.text_color.svg_color()
        return self.text_color

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    def get_cell_x(self, col_index: int) -> float:
        x = self._ll.x
        for i in range(col_index):
            x += self.column_widths[i]
        return x

    def get_row_y(self, row_index: int) -> float:
        return self._ll.y - self.total_height + self.title_height + row_index * self.row_height


class KeyValueTable:
    """A simple two-column key-value table.

    Useful for property displays, configuration views, etc.
    """

    def __init__(
        self,
        parent: "Diagram",
        ll: PointLike,
        items: List[Tuple[str, str]],
        key_width: Optional[float] = None,
        value_width: Optional[float] = None,
        row_height: float = 22,
        font_size: float = 12,
        font_family: str = "sans-serif",
        padding: float = 6,
        fill: Optional[ColorLike] = None,
        stroke: Optional[ColorLike] = None,
        stroke_width: float = 1,
        key_fill: Optional[ColorLike] = None,
        key_text_color: Optional[ColorLike] = None,
        value_text_color: Optional[ColorLike] = None,
    ):
        self._ll = Point.resolve_point(ll)
        self.items = items
        self.row_height = row_height
        self.font_size = font_size
        self.font_family = font_family
        self.padding = padding
        self.fill = Color.resolve_color(fill) if fill is not None else None
        self.stroke = Color.resolve_color(stroke) if stroke is not None else Color("#000000")
        self.stroke_width = stroke_width
        self.key_fill = Color.resolve_color(key_fill) if key_fill is not None else None
        self.key_text_color = Color.resolve_color(key_text_color) if key_text_color is not None else Color("#000000")
        self.value_text_color = Color.resolve_color(value_text_color) if value_text_color is not None else Color("#000000")
        self.parent = parent

        if key_width is not None:
            self.key_width = key_width
        else:
            max_key = max(len(k) for k, v in items) if items else 5
            self.key_width = max_key * font_size * 0.6 + padding * 2

        if value_width is not None:
            self.value_width = value_width
        else:
            max_val = max(len(v) for k, v in items) if items else 10
            self.value_width = max_val * font_size * 0.6 + padding * 2

        parent.add_shape(self)

    @property
    def total_width(self) -> float:
        return self.key_width + self.value_width

    @property
    def total_height(self) -> float:
        return len(self.items) * self.row_height

    @property
    def x(self) -> float:
        return self._ll.x

    @property
    def y(self) -> float:
        return self._ll.y - self.total_height

    @property
    def width(self) -> float:
        return self.total_width

    @property
    def height(self) -> float:
        return self.total_height

    @property
    def bbox(self) -> BBox:
        return BBox(
            ll=Point(self._ll.x, self._ll.y),
            ur=Point(self._ll.x + self.total_width, self._ll.y - self.total_height),
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
    def key_fill_color(self) -> Optional[str]:
        if self.key_fill is None:
            return None
        if isinstance(self.key_fill, Color):
            return self.key_fill.svg_color()
        return self.key_fill

    @property
    def key_text_color_str(self) -> str:
        if isinstance(self.key_text_color, Color):
            return self.key_text_color.svg_color()
        return self.key_text_color

    @property
    def value_text_color_str(self) -> str:
        if isinstance(self.value_text_color, Color):
            return self.value_text_color.svg_color()
        return self.value_text_color

    def bounding_box(self) -> Tuple[float, float, float, float]:
        bbox = self.bbox
        return (bbox.ll.x, bbox.ur.y, bbox.ur.x, bbox.ll.y)

    def get_row_y(self, row_index: int) -> float:
        return self._ll.y - self.total_height + row_index * self.row_height
