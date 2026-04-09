"""
SVG backend for OD-DO.

Renders diagrams to SVG format with support for shapes, paths, and Color objects.
"""

from typing import List, Union, Optional, Dict, Tuple, TYPE_CHECKING
from .base import Backend
from ...shapes.base import Shape, Rectangle, Circle, OpenBlock
from ...shapes.ellipse import Ellipse
from ...shapes.curves import CurveBase, QuadraticBezier, CubicBezier, Arc, SemiCircle
from ...shapes.polygon import RegularPolygon, Star
from ...shapes.image import Image
from ...shapes.annotations import DimensionLine, LeaderLine, Callout
from ...shapes.flowchart import (
    Diamond as DiamondShape,
    Parallelogram,
    Document,
    Cylinder,
    Cloud,
    Terminator,
)
from ...shapes.text import Text, TextBox, Label
from ...shapes.table import Table, EntityTable, KeyValueTable
from ...colors import Color
from ...markers import Marker, Arrow, Circle as CircleMarker, Square, Diamond, Bar

try:
    from diagram_libs.basic_circuit_elements.old.basic_shapes import (
        CircuitElement,
        Resistor as OldResistor,
        Capacitor,
        Inductor,
        Battery,
        Ground,
        Diode,
        Transistor,
        OpAmp,
        Switch,
        VoltageSource,
        CurrentSource,
        Fuse,
        Transformer,
    )
    from diagram_libs.basic_circuit_elements.old.logic_gates import (
        LogicGate,
        ANDGate,
        ORGate,
        XORGate,
        Buffer,
        DFlipFlop,
        Mux,
    )
    from diagram_libs.basic_circuit_elements.old.wires import (
        Wire,
        WireSegments,
        WireJump,
        WireJunction,
        Bus,
        BusTap,
        Label as CircuitLabel,
        PowerRail,
        GroundRail,
    )

    HAS_CIRCUIT_ELEMENTS = True
except ImportError:
    HAS_CIRCUIT_ELEMENTS = False

if TYPE_CHECKING:
    from ...placement import Placement
    from ...paths import Path, Line, StrokeLine


class SVGBackend(Backend):
    """Backend for rendering diagrams to SVG format."""

    def __init__(self):
        self._marker_defs: Dict[str, str] = {}
        self._marker_counter = 0
        self._stroke_line_mask_counter = 0

    def render(
        self,
        items: List[Union[Shape, "Placement", "Path"]],
        output_path: str,
        **kwargs,
    ) -> None:
        """Render items to an SVG file.

        Args:
            items: List of shapes, placements, and paths to render.
            output_path: Path to write the SVG file.
            **kwargs: Additional options:
                - width: SVG width in pixels
                - height: SVG height in pixels
                - unit_to_pixels: Scale factor for converting units to pixels
                - padding_left: Left padding in user units
                - padding_top: Top padding in user units
                - show_ruler: Show rulers on the outside of the diagram
                - units: Unit label for ruler (e.g., "um", "mm")
        """
        self._marker_defs = {}
        self._marker_counter = 0
        self._stroke_line_mask_counter = 0
        self._stroke_line_masks: Dict[int, str] = {}

        width = kwargs.get("width", 800)
        height = kwargs.get("height", 600)
        unit_to_pixels = kwargs.get("unit_to_pixels", 1.0)
        padding_left = kwargs.get("padding_left", 0)
        padding_top = kwargs.get("padding_top", 0)
        show_ruler = kwargs.get("show_ruler", False)
        show_grid = kwargs.get("show_grid", False)
        units = kwargs.get("units", "px")
        background = kwargs.get("background", None)

        ruler_size = 40 if show_ruler else 0

        offset_x, offset_y = self._calculate_content_offset(items)

        total_width = width + ruler_size
        total_height = height + ruler_size

        svg_content = f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background rectangle if specified
        if background is not None:
            from ...colors import Color

            bg_color = Color.resolve_color(background)
            bg_attr = self._get_color_attrs(bg_color, "fill", "white")
            svg_content += (
                f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" {bg_attr}/>\n'
            )

        if show_ruler:
            svg_content += self._render_rulers(
                width,
                height,
                ruler_size,
                unit_to_pixels,
                units,
                offset_x,
                offset_y,
                padding_left,
                padding_top,
            )

        translate_x = (padding_left - offset_x) * unit_to_pixels + ruler_size
        translate_y = (padding_top - offset_y) * unit_to_pixels + ruler_size

        items_svg = ""
        if unit_to_pixels != 1.0 or translate_x != 0 or translate_y != 0:
            items_svg += f'  <g transform="translate({translate_x}, {translate_y}) scale({unit_to_pixels})">\n'
            for item in items:
                items_svg += self._item_to_svg(item)
            items_svg += "  </g>\n"
        else:
            for item in items:
                items_svg += self._item_to_svg(item)

        if self._marker_defs or self._stroke_line_masks:
            svg_content += "  <defs>\n"
            for marker_svg in self._marker_defs.values():
                svg_content += marker_svg
            for mask_svg in self._stroke_line_masks.values():
                svg_content += mask_svg
            svg_content += "  </defs>\n"

        svg_content += items_svg

        if show_grid:
            svg_content += self._render_grid(
                width,
                height,
                ruler_size,
                unit_to_pixels,
                offset_x,
                offset_y,
                padding_left,
                padding_top,
            )

        svg_content += "</svg>"

        with open(output_path, "w") as f:
            f.write(svg_content)

    def _calculate_content_offset(
        self,
        items: List[Union[Shape, "Placement", "Path"]],
    ) -> tuple:
        """Calculate the minimum x,y of all content to determine offset."""
        from ...placement import Placement

        if not items:
            return (0, 0)

        min_x = float("inf")
        min_y = float("inf")

        for item in items:
            if isinstance(item, Placement):
                # Use the rotated bounding box
                bbox = item.get_bounding_box()
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
            else:
                bbox = item.bounding_box()
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])

        if min_x == float("inf"):
            return (0, 0)

        return (min_x, min_y)

    def _render_rulers(
        self,
        content_width: float,
        content_height: float,
        ruler_size: float,
        unit_to_pixels: float,
        units: str,
        offset_x: float,
        offset_y: float,
        padding_left: float,
        padding_top: float,
    ) -> str:
        """Render rulers on the left and top edges of the diagram."""
        font = 'font-family="system-ui, -apple-system, sans-serif"'
        svg = ""
        svg += f'  <rect x="0" y="0" width="{ruler_size}" height="{ruler_size + content_height}" fill="#f5f5f5"/>\n'
        svg += f'  <rect x="0" y="0" width="{ruler_size + content_width}" height="{ruler_size}" fill="#f5f5f5"/>\n'
        svg += f'  <line x1="{ruler_size}" y1="0" x2="{ruler_size}" y2="{ruler_size + content_height}" stroke="#ccc" stroke-width="1"/>\n'
        svg += f'  <line x1="0" y1="{ruler_size}" x2="{ruler_size + content_width}" y2="{ruler_size}" stroke="#ccc" stroke-width="1"/>\n'

        tick_interval_units = self._calculate_tick_interval(content_width / unit_to_pixels)
        tick_interval_px = tick_interval_units * unit_to_pixels
        minor_tick_interval_px = tick_interval_px / 2
        micro_tick_interval_px = tick_interval_px / 4

        content_start_units = offset_x - padding_left
        first_tick_units = (
            int(content_start_units / tick_interval_units) + 1
        ) * tick_interval_units
        first_tick_px = ruler_size + (first_tick_units - content_start_units) * unit_to_pixels

        mx = first_tick_px + micro_tick_interval_px
        while mx < ruler_size + content_width:
            dist_to_major = (mx - first_tick_px) % tick_interval_px
            dist_to_minor = (mx - first_tick_px - minor_tick_interval_px) % tick_interval_px
            if abs(dist_to_minor) < 0.5 or abs(dist_to_minor - tick_interval_px) < 0.5:
                svg += f'  <line x1="{mx}" y1="{ruler_size - 5}" x2="{mx}" y2="{ruler_size}" stroke="#999" stroke-width="1"/>\n'
            elif abs(dist_to_major) > 0.5 and abs(dist_to_major - tick_interval_px) > 0.5:
                svg += f'  <line x1="{mx}" y1="{ruler_size - 3}" x2="{mx}" y2="{ruler_size}" stroke="#bbb" stroke-width="1"/>\n'
            mx += micro_tick_interval_px

        x = first_tick_px
        tick_value = first_tick_units
        while x < ruler_size + content_width:
            svg += f'  <line x1="{x}" y1="{ruler_size - 8}" x2="{x}" y2="{ruler_size}" stroke="#666" stroke-width="1"/>\n'
            label = f"{tick_value:.0f}"
            svg += f'  <text x="{x}" y="{ruler_size - 12}" text-anchor="middle" font-size="9" {font} fill="#333">{label}</text>\n'
            if unit_to_pixels != 1.0:
                px_value = tick_value * unit_to_pixels
                svg += f'  <text x="{x}" y="{ruler_size - 24}" text-anchor="middle" font-size="7" {font} fill="#888">{px_value:.0f}px</text>\n'
            x += tick_interval_px
            tick_value += tick_interval_units

        content_start_units_y = offset_y - padding_top
        first_tick_units_y = (
            int(content_start_units_y / tick_interval_units) + 1
        ) * tick_interval_units
        first_tick_px_y = ruler_size + (first_tick_units_y - content_start_units_y) * unit_to_pixels

        my = first_tick_px_y + micro_tick_interval_px
        while my < ruler_size + content_height:
            dist_to_major = (my - first_tick_px_y) % tick_interval_px
            dist_to_minor = (my - first_tick_px_y - minor_tick_interval_px) % tick_interval_px
            if abs(dist_to_minor) < 0.5 or abs(dist_to_minor - tick_interval_px) < 0.5:
                svg += f'  <line x1="{ruler_size - 5}" y1="{my}" x2="{ruler_size}" y2="{my}" stroke="#999" stroke-width="1"/>\n'
            elif abs(dist_to_major) > 0.5 and abs(dist_to_major - tick_interval_px) > 0.5:
                svg += f'  <line x1="{ruler_size - 3}" y1="{my}" x2="{ruler_size}" y2="{my}" stroke="#bbb" stroke-width="1"/>\n'
            my += micro_tick_interval_px

        y = first_tick_px_y
        tick_value = first_tick_units_y
        while y < ruler_size + content_height:
            svg += f'  <line x1="{ruler_size - 8}" y1="{y}" x2="{ruler_size}" y2="{y}" stroke="#666" stroke-width="1"/>\n'
            label = f"{tick_value:.0f}"
            if unit_to_pixels != 1.0:
                px_value = tick_value * unit_to_pixels
                svg += f'  <text x="{ruler_size - 10}" y="{y - 6}" text-anchor="end" font-size="7" {font} fill="#888">{px_value:.0f}px</text>\n'
                svg += f'  <text x="{ruler_size - 10}" y="{y + 4}" text-anchor="end" font-size="9" {font} fill="#333">{label}</text>\n'
            else:
                svg += f'  <text x="{ruler_size - 10}" y="{y + 4}" text-anchor="end" font-size="9" {font} fill="#333">{label}</text>\n'
            y += tick_interval_px
            tick_value += tick_interval_units

        if units != "px":
            svg += f'  <text x="4" y="14" font-size="9" {font} fill="#666">{units}</text>\n'
            if unit_to_pixels != 1.0:
                svg += f'  <text x="4" y="26" font-size="7" {font} fill="#888">({unit_to_pixels}px/{units})</text>\n'

        return svg

    def _calculate_tick_interval(self, content_size: float) -> float:
        """Calculate a nice tick interval for the ruler."""
        target_ticks = 8
        raw_interval = content_size / target_ticks
        magnitude = 10 ** int(f"{raw_interval:.0e}".split("e")[1])
        normalized = raw_interval / magnitude
        if normalized < 1.5:
            nice = 1
        elif normalized < 3.5:
            nice = 2
        elif normalized < 7.5:
            nice = 5
        else:
            nice = 10
        return nice * magnitude

    def _render_grid(
        self,
        content_width: float,
        content_height: float,
        ruler_size: float,
        unit_to_pixels: float,
        offset_x: float,
        offset_y: float,
        padding_left: float,
        padding_top: float,
    ) -> str:
        """Render a light grey grid overlay on the diagram."""
        svg = ""

        svg += f'  <rect x="{ruler_size}" y="{ruler_size}" width="{content_width}" height="{content_height}" fill="none" stroke="#999" stroke-width="1"/>\n'

        tick_interval_units = self._calculate_tick_interval(content_width / unit_to_pixels)
        tick_interval_px = tick_interval_units * unit_to_pixels
        minor_tick_interval_px = tick_interval_px / 2

        content_start_units = offset_x - padding_left
        first_tick_units = (
            int(content_start_units / tick_interval_units) + 1
        ) * tick_interval_units
        first_tick_px = ruler_size + (first_tick_units - content_start_units) * unit_to_pixels

        x = first_tick_px
        while x < ruler_size + content_width:
            svg += f'  <line x1="{x}" y1="{ruler_size}" x2="{x}" y2="{ruler_size + content_height}" stroke="#ccc" stroke-width="0.5"/>\n'
            x += tick_interval_px

        x = first_tick_px + minor_tick_interval_px
        while x < ruler_size + content_width:
            svg += f'  <line x1="{x}" y1="{ruler_size}" x2="{x}" y2="{ruler_size + content_height}" stroke="#e8e8e8" stroke-width="0.5"/>\n'
            x += tick_interval_px

        content_start_units_y = offset_y - padding_top
        first_tick_units_y = (
            int(content_start_units_y / tick_interval_units) + 1
        ) * tick_interval_units
        first_tick_px_y = ruler_size + (first_tick_units_y - content_start_units_y) * unit_to_pixels

        y = first_tick_px_y
        while y < ruler_size + content_height:
            svg += f'  <line x1="{ruler_size}" y1="{y}" x2="{ruler_size + content_width}" y2="{y}" stroke="#ccc" stroke-width="0.5"/>\n'
            y += tick_interval_px

        y = first_tick_px_y + minor_tick_interval_px
        while y < ruler_size + content_height:
            svg += f'  <line x1="{ruler_size}" y1="{y}" x2="{ruler_size + content_width}" y2="{y}" stroke="#e8e8e8" stroke-width="0.5"/>\n'
            y += tick_interval_px

        return svg

    def _item_to_svg(self, item: Union[Shape, "Placement", "Path"]) -> str:
        """Convert an item to SVG markup."""
        from ...placement import Placement
        from ...paths import Path

        if isinstance(item, Placement):
            return self._placement_to_svg(item)
        elif isinstance(item, Path):
            return self._path_to_svg(item)
        return self._shape_to_svg(item)

    def _placement_to_svg(self, placement: "Placement") -> str:
        """Convert a Placement to SVG group with transforms."""
        transforms = []

        if placement.x != 0 or placement.y != 0:
            transforms.append(f"translate({placement.x}, {placement.y})")

        if not placement.transform.is_identity():
            if placement.rotation_offset_x is not None and placement.rotation_offset_y is not None:
                pivot_x = placement.rotation_offset_x
                pivot_y = placement.rotation_offset_y
            else:
                pivot_x = 0
                pivot_y = 0

            transform_str = placement.transform.to_svg_transform(pivot_x, pivot_y)
            if transform_str:
                transforms.append(transform_str)

        transform_attr = ""
        if transforms:
            transform_attr = f' transform="{" ".join(transforms)}"'

        shapes_svg = ""
        for shape in placement.get_shapes():
            shapes_svg += self._item_to_svg(shape)

        return f"  <g{transform_attr}>\n{shapes_svg}  </g>\n"

    def _shape_to_svg(self, shape: Shape) -> str:
        """Convert a shape to SVG markup."""
        if isinstance(shape, Circle):
            return self._circle_to_svg(shape)
        elif isinstance(shape, OpenBlock):
            return self._open_block_to_svg(shape)
        elif isinstance(shape, Rectangle):
            return self._rectangle_to_svg(shape)
        elif isinstance(shape, Ellipse):
            return self._ellipse_to_svg(shape)
        elif isinstance(shape, CurveBase):
            return self._curve_to_svg(shape)
        elif isinstance(shape, Star):
            return self._polygon_to_svg(shape)
        elif isinstance(shape, RegularPolygon):
            return self._polygon_to_svg(shape)
        elif isinstance(shape, DimensionLine):
            return self._dimension_line_to_svg(shape)
        elif isinstance(shape, LeaderLine):
            return self._leader_line_to_svg(shape)
        elif isinstance(shape, Callout):
            return self._callout_to_svg(shape)
        elif isinstance(shape, Cylinder):
            return self._cylinder_to_svg(shape)
        elif isinstance(shape, DiamondShape):
            return self._diamond_shape_to_svg(shape)
        elif isinstance(shape, Parallelogram):
            return self._polygon_to_svg(shape)
        elif isinstance(shape, Document):
            return self._path_shape_to_svg(shape)
        elif isinstance(shape, Cloud):
            return self._path_shape_to_svg(shape)
        elif isinstance(shape, Terminator):
            return self._path_shape_to_svg(shape)
        elif isinstance(shape, Text):
            return self._text_to_svg(shape)
        elif isinstance(shape, TextBox):
            return self._textbox_to_svg(shape)
        elif isinstance(shape, Label):
            return self._label_to_svg(shape)
        elif isinstance(shape, Table):
            return self._table_to_svg(shape)
        elif isinstance(shape, EntityTable):
            return self._entity_table_to_svg(shape)
        elif isinstance(shape, KeyValueTable):
            return self._keyvalue_table_to_svg(shape)
        elif isinstance(shape, Image):
            return self._image_to_svg(shape)
        if HAS_CIRCUIT_ELEMENTS:
            if isinstance(shape, WireJunction):
                return self._wire_junction_to_svg(shape)
            elif isinstance(shape, CircuitLabel):
                return self._circuit_label_to_svg(shape)
            elif isinstance(
                shape, (Wire, WireSegments, WireJump, Bus, BusTap, PowerRail, GroundRail)
            ):
                return self._circuit_wire_to_svg(shape)
            elif isinstance(shape, OpAmp):
                return self._opamp_to_svg(shape)
            elif isinstance(shape, (LogicGate, DFlipFlop, Mux)):
                return self._logic_gate_to_svg(shape)
            elif isinstance(shape, CircuitElement):
                return self._circuit_element_to_svg(shape)
        return ""

    def _get_color_attrs(
        self,
        color: Optional[Union[str, Color]],
        attr_name: str,
        default: str = "none",
    ) -> str:
        """Get SVG color attribute string with opacity if needed.

        Args:
            color: Color value (string, Color object, or None).
            attr_name: Attribute name ("fill" or "stroke").
            default: Default value if color is None.

        Returns:
            SVG attribute string like 'fill="#FF0000"' or 'fill="#FF0000" fill-opacity="0.5"'
        """
        if color is None:
            return f'{attr_name}="{default}"'

        if isinstance(color, Color):
            color_str = color.hex_rgb
            if color.a < 1.0:
                return f'{attr_name}="{color_str}" {attr_name}-opacity="{color.a}"'
            return f'{attr_name}="{color_str}"'

        return f'{attr_name}="{color}"'

    def _rectangle_to_svg(self, rect: Rectangle) -> str:
        """Convert a rectangle to SVG markup.

        Draws fill and stroke as separate elements to avoid overlap artifacts
        with semi-transparent colors. The stroke is drawn outside the fill.
        """
        sw = rect.stroke_width
        corner_radius = rect.corner_radius

        result = ""

        if rect.fill is not None:
            fill_attr = self._get_color_attrs(rect.fill, "fill", "none")
            fill_x = rect.x + sw
            fill_y = rect.y + sw
            fill_w = rect.width - 2 * sw
            fill_h = rect.height - 2 * sw
            fill_radius = max(0, corner_radius - sw) if corner_radius else None
            fill_radius_attr = f' rx="{fill_radius}" ry="{fill_radius}"' if fill_radius else ""
            result += (
                f'  <rect x="{fill_x}" y="{fill_y}" '
                f'width="{fill_w}" height="{fill_h}"{fill_radius_attr} '
                f'{fill_attr} stroke="none"/>\n'
            )

        if rect.stroke is not None:
            stroke_attr = self._get_color_attrs(rect.stroke, "stroke", "black")
            stroke_x = rect.x + sw / 2
            stroke_y = rect.y + sw / 2
            stroke_w = rect.width - sw
            stroke_h = rect.height - sw
            stroke_radius = max(0, corner_radius - sw / 2) if corner_radius else None
            stroke_radius_attr = (
                f' rx="{stroke_radius}" ry="{stroke_radius}"' if stroke_radius else ""
            )
            result += (
                f'  <rect x="{stroke_x}" y="{stroke_y}" '
                f'width="{stroke_w}" height="{stroke_h}"{stroke_radius_attr} '
                f'fill="none" {stroke_attr} stroke-width="{sw}"/>\n'
            )

        return result

    def _circle_to_svg(self, circle: Circle) -> str:
        """Convert a circle to SVG markup.

        Draws fill and stroke as separate elements to avoid overlap artifacts
        with semi-transparent colors. The stroke is drawn outside the fill.
        """
        cx = circle.x + circle.radius
        cy = circle.y + circle.radius
        sw = circle.stroke_width

        result = ""

        if circle.fill is not None:
            fill_attr = self._get_color_attrs(circle.fill, "fill", "none")
            fill_r = circle.radius - sw
            result += (
                f'  <circle cx="{cx}" cy="{cy}" r="{fill_r}" ' f'{fill_attr} stroke="none"/>\n'
            )

        if circle.stroke is not None:
            stroke_attr = self._get_color_attrs(circle.stroke, "stroke", "black")
            stroke_r = circle.radius - sw / 2
            result += (
                f'  <circle cx="{cx}" cy="{cy}" r="{stroke_r}" '
                f'fill="none" {stroke_attr} stroke-width="{sw}"/>\n'
            )

        return result

    def _open_block_to_svg(self, block: OpenBlock) -> str:
        """Convert an OpenBlock to SVG markup.

        Renders fill as a closed rect, stroke as a 3-sided path.
        """
        result = ""

        # Fill is a full rectangle
        if block.fill is not None:
            fill_attr = self._get_color_attrs(block.fill, "fill", "none")
            result += (
                f'  <rect x="{block.x}" y="{block.y}" '
                f'width="{block.width}" height="{block.height}" '
                f'{fill_attr} stroke="none"/>\n'
            )

        # Stroke is a 3-sided path
        if block.stroke is not None:
            stroke_attr = self._get_color_attrs(block.stroke, "stroke", "black")
            path = block.svg_path()
            result += (
                f'  <path d="{path}" '
                f'fill="none" {stroke_attr} stroke-width="{block.stroke_width}"/>\n'
            )

        return result

    def _path_to_svg(self, path: "Path") -> str:
        """Convert a path to SVG markup."""
        from ...paths import Line, StrokeLine

        if isinstance(path, StrokeLine):
            return self._stroke_line_to_svg(path)
        if isinstance(path, Line):
            return self._line_to_svg(path)
        return ""

    def _line_to_svg(self, line: "Line") -> str:
        """Convert a line (polyline) to SVG markup."""
        points = line.all_points
        if len(points) < 2:
            return ""

        points_str = " ".join(f"{p.x},{p.y}" for p in points)

        stroke_attr = self._get_color_attrs(line.color, "stroke", "black")

        dash_attr = ""
        if line.dash_pattern:
            dash_str = ",".join(str(v) for v in line.dash_pattern)
            dash_attr = f' stroke-dasharray="{dash_str}"'

        marker_attrs = ""
        if line.start_marker:
            marker_id = self._get_or_create_marker(
                line.start_marker, line.color, line.width, is_start=True
            )
            marker_attrs += f' marker-start="url(#{marker_id})"'
        if line.end_marker:
            marker_id = self._get_or_create_marker(
                line.end_marker, line.color, line.width, is_start=False
            )
            marker_attrs += f' marker-end="url(#{marker_id})"'

        return (
            f'  <polyline points="{points_str}" '
            f'fill="none" {stroke_attr} stroke-width="{line.width}"{dash_attr}{marker_attrs}/>\n'
        )

    def _stroke_line_to_svg(self, line: "StrokeLine") -> str:
        """Convert a stroke line to SVG markup.

        Renders as three separate non-overlapping lines:
        - Left edge stroke (offset left from center path)
        - Right edge stroke (offset right from center path)
        - Center fill line

        This prevents colors from mixing when using semi-transparent colors.
        """
        points = line.all_points
        if len(points) < 2:
            return ""

        edge_stroke_attr = self._get_color_attrs(line.edge_stroke_color, "stroke", "black")
        fill_stroke_attr = self._get_color_attrs(line.color, "stroke", "black")

        dash_attr = ""
        if line.dash_pattern:
            dash_str = ",".join(str(v) for v in line.dash_pattern)
            dash_attr = f' stroke-dasharray="{dash_str}"'

        inner_width = line.width - 2 * line.edge_stroke_width
        edge_offset = inner_width / 2 + line.edge_stroke_width / 2

        left_points = self._offset_polyline(points, edge_offset)
        right_points = self._offset_polyline(points, -edge_offset)

        center_str = " ".join(f"{p.x},{p.y}" for p in points)
        left_str = " ".join(f"{p.x},{p.y}" for p in left_points)
        right_str = " ".join(f"{p.x},{p.y}" for p in right_points)

        left_edge = (
            f'  <polyline points="{left_str}" '
            f'fill="none" {edge_stroke_attr} stroke-width="{line.edge_stroke_width}"{dash_attr}/>\n'
        )
        right_edge = (
            f'  <polyline points="{right_str}" '
            f'fill="none" {edge_stroke_attr} stroke-width="{line.edge_stroke_width}"{dash_attr}/>\n'
        )
        center_fill = (
            f'  <polyline points="{center_str}" '
            f'fill="none" {fill_stroke_attr} stroke-width="{inner_width}"{dash_attr}/>\n'
        )

        return left_edge + right_edge + center_fill

    def _offset_polyline(self, points: list, offset: float) -> list:
        """Offset a polyline by a perpendicular distance.

        Positive offset = left side (when traveling along the path)
        Negative offset = right side
        """
        import math
        from ...geometry import Point

        if len(points) < 2:
            return points

        result = []

        for i, pt in enumerate(points):
            if i == 0:
                dx = points[1].x - pt.x
                dy = points[1].y - pt.y
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    perp_x = -dy / length
                    perp_y = dx / length
                else:
                    perp_x, perp_y = 0, 0
                result.append(Point(pt.x + perp_x * offset, pt.y + perp_y * offset))

            elif i == len(points) - 1:
                dx = pt.x - points[i - 1].x
                dy = pt.y - points[i - 1].y
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    perp_x = -dy / length
                    perp_y = dx / length
                else:
                    perp_x, perp_y = 0, 0
                result.append(Point(pt.x + perp_x * offset, pt.y + perp_y * offset))

            else:
                dx1 = pt.x - points[i - 1].x
                dy1 = pt.y - points[i - 1].y
                len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)

                dx2 = points[i + 1].x - pt.x
                dy2 = points[i + 1].y - pt.y
                len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)

                if len1 > 0 and len2 > 0:
                    perp1_x = -dy1 / len1
                    perp1_y = dx1 / len1
                    perp2_x = -dy2 / len2
                    perp2_y = dx2 / len2

                    bisect_x = perp1_x + perp2_x
                    bisect_y = perp1_y + perp2_y
                    bisect_len = math.sqrt(bisect_x * bisect_x + bisect_y * bisect_y)

                    if bisect_len > 0.001:
                        bisect_x /= bisect_len
                        bisect_y /= bisect_len
                        dot = perp1_x * bisect_x + perp1_y * bisect_y
                        if abs(dot) > 0.001:
                            miter_length = offset / dot
                        else:
                            miter_length = offset
                        result.append(
                            Point(pt.x + bisect_x * miter_length, pt.y + bisect_y * miter_length)
                        )
                    else:
                        result.append(Point(pt.x + perp1_x * offset, pt.y + perp1_y * offset))
                else:
                    result.append(pt)

        return result

    def _get_color_str(self, color: Optional[Union[str, Color]], default: str = "black") -> str:
        """Get color as a string suitable for SVG, including alpha."""
        if color is None:
            return default
        if isinstance(color, Color):
            return color.svg_color()
        return color

    def _get_or_create_marker(
        self,
        marker: Marker,
        line_color: Optional[Union[str, Color]],
        line_width: float,
        is_start: bool,
    ) -> str:
        """Get or create an SVG marker definition, returning its ID."""
        effective_color = marker.get_color(line_color)
        color_str = self._get_color_str(effective_color)
        resolved_size = marker.get_size(line_width)
        resolved_length = marker.get_length()

        marker_key = (
            type(marker).__name__,
            resolved_size,
            resolved_length,
            color_str,
            marker.filled,
            is_start,
            getattr(marker, "style", None),
            getattr(marker, "invert", False),
            line_width if getattr(marker, "invert", False) else None,
        )

        if marker_key in self._marker_defs:
            return f"{marker.svg_id_prefix()}-{hash(marker_key) & 0xFFFFFFFF:08x}"

        self._marker_counter += 1
        marker_id = f"{marker.svg_id_prefix()}-{hash(marker_key) & 0xFFFFFFFF:08x}"

        marker_svg = self._create_marker_svg(
            marker, marker_id, resolved_size, resolved_length, color_str, is_start, line_width
        )
        self._marker_defs[marker_key] = marker_svg

        return marker_id

    def _create_marker_svg(
        self,
        marker: Marker,
        marker_id: str,
        size: float,
        length: float,
        color_str: str,
        is_start: bool,
        line_width: float,
    ) -> str:
        """Create the SVG markup for a marker definition."""
        fill = color_str if marker.filled else "none"
        stroke = color_str if not marker.filled else "none"

        orient = "auto-start-reverse" if is_start else "auto"

        if isinstance(marker, Arrow):
            return self._create_arrow_marker_svg(
                marker, marker_id, size, length, fill, stroke, orient, line_width
            )
        elif isinstance(marker, CircleMarker):
            return self._create_circle_marker_svg(marker_id, size, fill, stroke)
        elif isinstance(marker, Square):
            return self._create_square_marker_svg(marker_id, size, fill, stroke, orient)
        elif isinstance(marker, Diamond):
            return self._create_diamond_marker_svg(marker_id, size, fill, stroke)
        elif isinstance(marker, Bar):
            return self._create_bar_marker_svg(marker_id, size, stroke)

        return ""

    def _create_arrow_marker_svg(
        self,
        marker: Arrow,
        marker_id: str,
        size: float,
        length: float,
        fill: str,
        stroke: str,
        orient: str,
        line_width: float,
    ) -> str:
        """Create SVG for an arrow marker.

        Arrow base is at refX=0, tip points outward at x=w.
        This places the arrow base at the line endpoint.
        Size controls the height (base width), length controls how pointy.
        When invert=True, the arrow is a trapezoid with a flat edge matching the line width.
        """
        h = size * 0.6
        w = h * length

        stroke_attr = f'stroke="{stroke}"' if stroke != "none" else 'stroke="none"'

        if marker.invert:
            flat_half = line_width / 2
            top_y = h / 2 - flat_half
            bot_y = h / 2 + flat_half
            cut_amount = line_width * w / h
            w = w - cut_amount
            if marker.style == "open":
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <polyline points="{w},0 0,{top_y} 0,{bot_y} {w},{h}" '
                    f'fill="none" stroke="{stroke}" stroke-width="1.5"/>\n'
                    f"    </marker>\n"
                )
            elif marker.style == "barbed":
                mid_x = w * 0.7
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <path d="M{w},0 L0,{top_y} L0,{bot_y} L{w},{h} L{mid_x},{h/2} Z" '
                    f'fill="{fill}" {stroke_attr}/>\n'
                    f"    </marker>\n"
                )
            else:
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <polygon points="{w},0 0,{top_y} 0,{bot_y} {w},{h}" '
                    f'fill="{fill}" {stroke_attr}/>\n'
                    f"    </marker>\n"
                )
        else:
            if marker.style == "open":
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <polyline points="0,0 {w},{h/2} 0,{h}" '
                    f'fill="none" stroke="{stroke}" stroke-width="1.5"/>\n'
                    f"    </marker>\n"
                )
            elif marker.style == "barbed":
                mid_x = w * 0.3
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <path d="M0,0 L{w},{h/2} L0,{h} L{mid_x},{h/2} Z" '
                    f'fill="{fill}" {stroke_attr}/>\n'
                    f"    </marker>\n"
                )
            else:
                return (
                    f'    <marker id="{marker_id}" markerWidth="{w}" markerHeight="{h}" '
                    f'refX="0" refY="{h/2}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
                    f'      <polygon points="0,0 {w},{h/2} 0,{h}" '
                    f'fill="{fill}" {stroke_attr}/>\n'
                    f"    </marker>\n"
                )

    def _create_circle_marker_svg(
        self,
        marker_id: str,
        size: float,
        fill: str,
        stroke: str,
    ) -> str:
        """Create SVG for a circle marker."""
        r = size / 2
        return (
            f'    <marker id="{marker_id}" markerWidth="{size}" markerHeight="{size}" '
            f'refX="{r}" refY="{r}" markerUnits="userSpaceOnUse">\n'
            f'      <circle cx="{r}" cy="{r}" r="{r - 0.5}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>\n'
            f"    </marker>\n"
        )

    def _create_square_marker_svg(
        self,
        marker_id: str,
        size: float,
        fill: str,
        stroke: str,
        orient: str,
    ) -> str:
        """Create SVG for a square marker.

        Square is positioned adjacent to the line endpoint (not overlapping).
        refX=0 places the left edge at the endpoint; orient handles start vs end.
        """
        half = size / 2
        return (
            f'    <marker id="{marker_id}" markerWidth="{size}" markerHeight="{size}" '
            f'refX="0" refY="{half}" orient="{orient}" markerUnits="userSpaceOnUse">\n'
            f'      <rect x="0" y="0" width="{size}" height="{size}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>\n'
            f"    </marker>\n"
        )

    def _create_diamond_marker_svg(
        self,
        marker_id: str,
        size: float,
        fill: str,
        stroke: str,
    ) -> str:
        """Create SVG for a diamond marker."""
        half = size / 2
        return (
            f'    <marker id="{marker_id}" markerWidth="{size}" markerHeight="{size}" '
            f'refX="{half}" refY="{half}" markerUnits="userSpaceOnUse">\n'
            f'      <polygon points="{half},0 {size},{half} {half},{size} 0,{half}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>\n'
            f"    </marker>\n"
        )

    def _create_bar_marker_svg(
        self,
        marker_id: str,
        size: float,
        stroke: str,
    ) -> str:
        """Create SVG for a bar (perpendicular line) marker."""
        half = size / 2
        return (
            f'    <marker id="{marker_id}" markerWidth="4" markerHeight="{size}" '
            f'refX="2" refY="{half}" markerUnits="userSpaceOnUse">\n'
            f'      <line x1="2" y1="0" x2="2" y2="{size}" '
            f'stroke="{stroke}" stroke-width="2"/>\n'
            f"    </marker>\n"
        )

    def _ellipse_to_svg(self, ellipse: Ellipse) -> str:
        """Convert an ellipse to SVG markup."""
        cx = ellipse.center.x
        cy = ellipse.center.y
        sw = ellipse.stroke_width

        result = ""

        if ellipse.fill is not None:
            fill_attr = self._get_color_attrs(ellipse.fill, "fill", "none")
            fill_rx = ellipse.radius_x - sw
            fill_ry = ellipse.radius_y - sw
            result += (
                f'  <ellipse cx="{cx}" cy="{cy}" rx="{fill_rx}" ry="{fill_ry}" '
                f'{fill_attr} stroke="none"/>\n'
            )

        if ellipse.stroke is not None:
            stroke_attr = self._get_color_attrs(ellipse.stroke, "stroke", "black")
            stroke_rx = ellipse.radius_x - sw / 2
            stroke_ry = ellipse.radius_y - sw / 2
            result += (
                f'  <ellipse cx="{cx}" cy="{cy}" rx="{stroke_rx}" ry="{stroke_ry}" '
                f'fill="none" {stroke_attr} stroke-width="{sw}"/>\n'
            )

        return result

    def _curve_to_svg(self, curve: CurveBase) -> str:
        """Convert a curve (Bezier, Arc, SemiCircle) to SVG markup."""
        fill_attr = self._get_color_attrs(curve.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(curve.stroke, "stroke", "black")
        return (
            f'  <path d="{curve.svg_path()}" '
            f'{fill_attr} {stroke_attr} stroke-width="{curve.stroke_width}"/>\n'
        )

    def _polygon_to_svg(self, poly) -> str:
        """Convert a polygon (RegularPolygon, Star, Parallelogram) to SVG markup."""
        fill_attr = self._get_color_attrs(poly.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(poly.stroke, "stroke", "black")
        return (
            f'  <polygon points="{poly.svg_points()}" '
            f'{fill_attr} {stroke_attr} stroke-width="{poly.stroke_width}"/>\n'
        )

    def _dimension_line_to_svg(self, dim: DimensionLine) -> str:
        """Convert a dimension line to SVG markup."""
        stroke_attr = self._get_color_attrs(dim.stroke, "stroke", "black")
        sw = dim.stroke_width
        tick = dim.tick_size

        ds = dim.dimension_start
        de = dim.dimension_end
        esi = dim.extension_line_start_inner
        eso = dim.extension_line_start_outer
        eei = dim.extension_line_end_inner
        eeo = dim.extension_line_end_outer

        d = dim._direction
        perp = dim._perpendicular

        tick_s1 = (ds.x - perp.x * tick / 2, ds.y - perp.y * tick / 2)
        tick_s2 = (ds.x + perp.x * tick / 2, ds.y + perp.y * tick / 2)
        tick_e1 = (de.x - perp.x * tick / 2, de.y - perp.y * tick / 2)
        tick_e2 = (de.x + perp.x * tick / 2, de.y + perp.y * tick / 2)

        return (
            f'  <line x1="{ds.x}" y1="{ds.y}" x2="{de.x}" y2="{de.y}" '
            f'{stroke_attr} stroke-width="{sw}"/>\n'
            f'  <line x1="{esi.x}" y1="{esi.y}" x2="{eso.x}" y2="{eso.y}" '
            f'{stroke_attr} stroke-width="{sw}"/>\n'
            f'  <line x1="{eei.x}" y1="{eei.y}" x2="{eeo.x}" y2="{eeo.y}" '
            f'{stroke_attr} stroke-width="{sw}"/>\n'
            f'  <line x1="{tick_s1[0]}" y1="{tick_s1[1]}" x2="{tick_s2[0]}" y2="{tick_s2[1]}" '
            f'{stroke_attr} stroke-width="{sw}"/>\n'
            f'  <line x1="{tick_e1[0]}" y1="{tick_e1[1]}" x2="{tick_e2[0]}" y2="{tick_e2[1]}" '
            f'{stroke_attr} stroke-width="{sw}"/>\n'
        )

    def _leader_line_to_svg(self, leader: LeaderLine) -> str:
        """Convert a leader line to SVG markup."""
        stroke_attr = self._get_color_attrs(leader.stroke, "stroke", "black")
        pts = leader.path_points
        points_str = " ".join(f"{p.x},{p.y}" for p in pts)

        arrow_svg = ""
        if leader.arrow_size > 0 and len(pts) >= 2:
            p0, p1 = pts[0], pts[1]
            dx = p1.x - p0.x
            dy = p1.y - p0.y
            length = (dx * dx + dy * dy) ** 0.5
            if length > 0:
                dx, dy = dx / length, dy / length
                size = leader.arrow_size
                ax1 = p0.x + dx * size - dy * size * 0.4
                ay1 = p0.y + dy * size + dx * size * 0.4
                ax2 = p0.x + dx * size + dy * size * 0.4
                ay2 = p0.y + dy * size - dx * size * 0.4
                stroke_color = leader.stroke_color if leader.stroke_color else "black"
                arrow_svg = (
                    f'  <polygon points="{p0.x},{p0.y} {ax1},{ay1} {ax2},{ay2}" '
                    f'fill="{stroke_color}" stroke="none"/>\n'
                )

        return (
            f'  <polyline points="{points_str}" '
            f'fill="none" {stroke_attr} stroke-width="{leader.stroke_width}"/>\n'
            f"{arrow_svg}"
        )

    def _callout_to_svg(self, callout: Callout) -> str:
        """Convert a callout to SVG markup."""
        fill_attr = self._get_color_attrs(callout.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(callout.stroke, "stroke", "black")
        return (
            f'  <path d="{callout.svg_path()}" '
            f'{fill_attr} {stroke_attr} stroke-width="{callout.stroke_width}"/>\n'
        )

    def _cylinder_to_svg(self, cyl: Cylinder) -> str:
        """Convert a cylinder to SVG markup."""
        fill_attr = self._get_color_attrs(cyl.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(cyl.stroke, "stroke", "black")

        body_path = cyl.svg_body_path()
        top_path = cyl.svg_top_path()

        return (
            f'  <path d="{body_path}" '
            f'{fill_attr} {stroke_attr} stroke-width="{cyl.stroke_width}"/>\n'
            f'  <path d="{top_path}" '
            f'{fill_attr} {stroke_attr} stroke-width="{cyl.stroke_width}"/>\n'
        )

    def _diamond_shape_to_svg(self, diamond: DiamondShape) -> str:
        """Convert a diamond shape to SVG markup."""
        fill_attr = self._get_color_attrs(diamond.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(diamond.stroke, "stroke", "black")
        return (
            f'  <polygon points="{diamond.svg_points()}" '
            f'{fill_attr} {stroke_attr} stroke-width="{diamond.stroke_width}"/>\n'
        )

    def _path_shape_to_svg(self, shape) -> str:
        """Convert a path-based shape (Document, Cloud, Terminator) to SVG markup."""
        fill_attr = self._get_color_attrs(shape.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(shape.stroke, "stroke", "black")
        return (
            f'  <path d="{shape.svg_path()}" '
            f'{fill_attr} {stroke_attr} stroke-width="{shape.stroke_width}"/>\n'
        )

    def _text_to_svg(self, text: Text) -> str:
        """Convert a Text element to SVG markup."""
        lines = text.lines
        if not lines:
            return ""

        font_attrs = (
            f'font-family="{text.font_family}" '
            f'font-size="{text.font_size}" '
            f'font-weight="{text.font_weight}"'
        )
        fill_color = text.fill_color if text.fill_color else "black"

        if len(lines) == 1:
            return (
                f'  <text x="{text.position.x}" y="{text.position.y}" '
                f'text-anchor="{text.text_anchor}" '
                f'dominant-baseline="{text.dominant_baseline}" '
                f'{font_attrs} fill="{fill_color}">{self._escape_xml(lines[0])}</text>\n'
            )

        result = (
            f'  <text x="{text.position.x}" y="{text.position.y}" '
            f'text-anchor="{text.text_anchor}" '
            f'{font_attrs} fill="{fill_color}">\n'
        )
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else text.line_height
            baseline = f'dominant-baseline="{text.dominant_baseline}"' if i == 0 else ""
            result += (
                f'    <tspan x="{text.position.x}" dy="{dy}" {baseline}>'
                f"{self._escape_xml(line)}</tspan>\n"
            )
        result += "  </text>\n"
        return result

    def _textbox_to_svg(self, tb: TextBox) -> str:
        """Convert a TextBox to SVG markup."""
        result = ""
        corner_radius = tb.corner_radius
        radius_attr = f' rx="{corner_radius}" ry="{corner_radius}"' if corner_radius else ""

        if tb.fill is not None:
            fill_attr = self._get_color_attrs(tb.fill, "fill", "none")
            result += (
                f'  <rect x="{tb.x}" y="{tb.y}" '
                f'width="{tb.width}" height="{tb.height}"{radius_attr} '
                f'{fill_attr} stroke="none"/>\n'
            )

        if tb.stroke is not None:
            stroke_attr = self._get_color_attrs(tb.stroke, "stroke", "black")
            result += (
                f'  <rect x="{tb.x}" y="{tb.y}" '
                f'width="{tb.width}" height="{tb.height}"{radius_attr} '
                f'fill="none" {stroke_attr} stroke-width="{tb.stroke_width}"/>\n'
            )

        font_attrs = (
            f'font-family="{tb.font_family}" '
            f'font-size="{tb.font_size}" '
            f'font-weight="{tb.font_weight}"'
        )
        text_color = tb.text_fill_color

        lines = tb.lines
        if len(lines) == 1:
            result += (
                f'  <text x="{tb.text_x}" y="{tb.text_y}" '
                f'text-anchor="{tb.text_anchor}" '
                f'{font_attrs} fill="{text_color}">{self._escape_xml(lines[0])}</text>\n'
            )
        else:
            result += (
                f'  <text x="{tb.text_x}" y="{tb.text_y}" '
                f'text-anchor="{tb.text_anchor}" '
                f'{font_attrs} fill="{text_color}">\n'
            )
            for i, line in enumerate(lines):
                dy = 0 if i == 0 else tb.line_height
                result += (
                    f'    <tspan x="{tb.text_x}" dy="{dy}">' f"{self._escape_xml(line)}</tspan>\n"
                )
            result += "  </text>\n"

        return result

    def _label_to_svg(self, label: Label) -> str:
        """Convert a Label to SVG markup."""
        result = ""
        corner_radius = label.corner_radius
        radius_attr = f' rx="{corner_radius}" ry="{corner_radius}"' if corner_radius else ""

        if label.fill is not None or label.stroke is not None:
            if label.fill is not None:
                fill_attr = self._get_color_attrs(label.fill, "fill", "none")
                result += (
                    f'  <rect x="{label.box_x}" y="{label.box_y}" '
                    f'width="{label.width}" height="{label.height}"{radius_attr} '
                    f'{fill_attr} stroke="none"/>\n'
                )
            if label.stroke is not None:
                stroke_attr = self._get_color_attrs(label.stroke, "stroke", "black")
                result += (
                    f'  <rect x="{label.box_x}" y="{label.box_y}" '
                    f'width="{label.width}" height="{label.height}"{radius_attr} '
                    f'fill="none" {stroke_attr} stroke-width="{label.stroke_width}"/>\n'
                )

        font_attrs = (
            f'font-family="{label.font_family}" '
            f'font-size="{label.font_size}" '
            f'font-weight="{label.font_weight}"'
        )
        text_color = label.text_fill_color

        lines = label.lines
        if len(lines) == 1:
            result += (
                f'  <text x="{label.text_x}" y="{label.text_y}" '
                f'text-anchor="{label.text_anchor}" '
                f'{font_attrs} fill="{text_color}">{self._escape_xml(lines[0])}</text>\n'
            )
        else:
            result += (
                f'  <text x="{label.text_x}" y="{label.text_y}" '
                f'text-anchor="{label.text_anchor}" '
                f'{font_attrs} fill="{text_color}">\n'
            )
            for i, line in enumerate(lines):
                dy = 0 if i == 0 else label.line_height
                result += (
                    f'    <tspan x="{label.text_x}" dy="{dy}">'
                    f"{self._escape_xml(line)}</tspan>\n"
                )
            result += "  </text>\n"

        return result

    def _table_to_svg(self, table: Table) -> str:
        """Convert a Table to SVG markup."""
        result = ""
        stroke_color = table.stroke_color if table.stroke_color else "black"
        sw = table.stroke_width
        font_attrs = f'font-family="{table.font_family}" font-size="{table.font_size}"'

        if table.fill_color:
            result += (
                f'  <rect x="{table.x}" y="{table.y}" '
                f'width="{table.width}" height="{table.height}" '
                f'fill="{table.fill_color}" stroke="none"/>\n'
            )

        if table.header_fill_color:
            result += (
                f'  <rect x="{table.x}" y="{table.y}" '
                f'width="{table.width}" height="{table.header_height}" '
                f'fill="{table.header_fill_color}" stroke="none"/>\n'
            )

        for row_idx in range(len(table.rows)):
            if table.alternate_fill_color and row_idx % 2 == 1:
                row_y = table.get_row_y(row_idx)
                result += (
                    f'  <rect x="{table.x}" y="{row_y}" '
                    f'width="{table.width}" height="{table.row_height}" '
                    f'fill="{table.alternate_fill_color}" stroke="none"/>\n'
                )

        result += (
            f'  <rect x="{table.x}" y="{table.y}" '
            f'width="{table.width}" height="{table.height}" '
            f'fill="none" stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        header_y = table.y + table.header_height
        result += (
            f'  <line x1="{table.x}" y1="{header_y}" '
            f'x2="{table.x + table.width}" y2="{header_y}" '
            f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        for row_idx in range(1, len(table.rows)):
            row_y = table.get_row_y(row_idx)
            result += (
                f'  <line x1="{table.x}" y1="{row_y}" '
                f'x2="{table.x + table.width}" y2="{row_y}" '
                f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
            )

        x = table.x
        for i in range(len(table.column_widths) - 1):
            x += table.column_widths[i]
            result += (
                f'  <line x1="{x}" y1="{table.y}" '
                f'x2="{x}" y2="{table.y + table.height}" '
                f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
            )

        for col_idx, col_name in enumerate(table.columns):
            cell_x = table.get_cell_x(col_idx) + table.padding
            cell_y = table.y + table.header_height / 2 + table.font_size * 0.35
            result += (
                f'  <text x="{cell_x}" y="{cell_y}" {font_attrs} '
                f'font-weight="bold" fill="{table.header_text_color_str}">'
                f"{self._escape_xml(col_name)}</text>\n"
            )

        for row_idx, row in enumerate(table.rows):
            row_y = table.get_row_y(row_idx)
            for col_idx, cell in enumerate(row):
                if col_idx < len(table.column_widths):
                    cell_x = table.get_cell_x(col_idx) + table.padding
                    cell_y = row_y + table.row_height / 2 + table.font_size * 0.35
                    result += (
                        f'  <text x="{cell_x}" y="{cell_y}" {font_attrs} '
                        f'fill="{table.text_color_str}">{self._escape_xml(cell)}</text>\n'
                    )

        return result

    def _entity_table_to_svg(self, entity: EntityTable) -> str:
        """Convert an EntityTable to SVG markup."""
        result = ""
        stroke_color = entity.stroke_color if entity.stroke_color else "black"
        sw = entity.stroke_width
        font_attrs = f'font-family="{entity.font_family}" font-size="{entity.font_size}"'

        result += (
            f'  <rect x="{entity.x}" y="{entity.y}" '
            f'width="{entity.width}" height="{entity.height}" '
            f'fill="{entity.fill_color}" stroke="none"/>\n'
        )

        result += (
            f'  <rect x="{entity.x}" y="{entity.y}" '
            f'width="{entity.width}" height="{entity.title_height}" '
            f'fill="{entity.title_fill_color}" stroke="none"/>\n'
        )

        result += (
            f'  <rect x="{entity.x}" y="{entity.y}" '
            f'width="{entity.width}" height="{entity.height}" '
            f'fill="none" stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        title_y = entity.y + entity.title_height
        result += (
            f'  <line x1="{entity.x}" y1="{title_y}" '
            f'x2="{entity.x + entity.width}" y2="{title_y}" '
            f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        title_text_y = entity.y + entity.title_height / 2 + entity.font_size * 0.35
        result += (
            f'  <text x="{entity.x + entity.width / 2}" y="{title_text_y}" '
            f'text-anchor="middle" {font_attrs} font-weight="bold" '
            f'fill="{entity.title_text_color_str}">{self._escape_xml(entity.title)}</text>\n'
        )

        for row_idx, (name, dtype, key) in enumerate(entity.rows):
            row_y = entity.get_row_y(row_idx)
            text_y = row_y + entity.row_height / 2 + entity.font_size * 0.35

            name_x = entity.get_cell_x(0) + entity.padding
            result += (
                f'  <text x="{name_x}" y="{text_y}" {font_attrs} '
                f'fill="{entity.text_color_str}">{self._escape_xml(name)}</text>\n'
            )

            type_x = entity.get_cell_x(1) + entity.padding
            result += (
                f'  <text x="{type_x}" y="{text_y}" {font_attrs} '
                f'fill="{entity.text_color_str}">{self._escape_xml(dtype)}</text>\n'
            )

            if key:
                key_x = entity.get_cell_x(2) + entity.padding
                result += (
                    f'  <text x="{key_x}" y="{text_y}" {font_attrs} '
                    f'font-weight="bold" fill="{entity.text_color_str}">'
                    f"{self._escape_xml(key)}</text>\n"
                )

        return result

    def _keyvalue_table_to_svg(self, kv: KeyValueTable) -> str:
        """Convert a KeyValueTable to SVG markup."""
        result = ""
        stroke_color = kv.stroke_color if kv.stroke_color else "black"
        sw = kv.stroke_width
        font_attrs = f'font-family="{kv.font_family}" font-size="{kv.font_size}"'

        if kv.fill_color:
            result += (
                f'  <rect x="{kv.x}" y="{kv.y}" '
                f'width="{kv.width}" height="{kv.height}" '
                f'fill="{kv.fill_color}" stroke="none"/>\n'
            )

        if kv.key_fill_color:
            result += (
                f'  <rect x="{kv.x}" y="{kv.y}" '
                f'width="{kv.key_width}" height="{kv.height}" '
                f'fill="{kv.key_fill_color}" stroke="none"/>\n'
            )

        result += (
            f'  <rect x="{kv.x}" y="{kv.y}" '
            f'width="{kv.width}" height="{kv.height}" '
            f'fill="none" stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        key_sep_x = kv.x + kv.key_width
        result += (
            f'  <line x1="{key_sep_x}" y1="{kv.y}" '
            f'x2="{key_sep_x}" y2="{kv.y + kv.height}" '
            f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
        )

        for row_idx in range(1, len(kv.items)):
            row_y = kv.get_row_y(row_idx)
            result += (
                f'  <line x1="{kv.x}" y1="{row_y}" '
                f'x2="{kv.x + kv.width}" y2="{row_y}" '
                f'stroke="{stroke_color}" stroke-width="{sw}"/>\n'
            )

        for row_idx, (key, value) in enumerate(kv.items):
            row_y = kv.get_row_y(row_idx)
            text_y = row_y + kv.row_height / 2 + kv.font_size * 0.35

            key_x = kv.x + kv.padding
            result += (
                f'  <text x="{key_x}" y="{text_y}" {font_attrs} '
                f'font-weight="bold" fill="{kv.key_text_color_str}">'
                f"{self._escape_xml(key)}</text>\n"
            )

            value_x = kv.x + kv.key_width + kv.padding
            result += (
                f'  <text x="{value_x}" y="{text_y}" {font_attrs} '
                f'fill="{kv.value_text_color_str}">{self._escape_xml(value)}</text>\n'
            )

        return result

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters in text."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _circuit_element_to_svg(self, elem) -> str:
        """Convert a circuit element to SVG markup."""
        fill_attr = self._get_color_attrs(elem.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(elem.stroke, "stroke", "black")
        path = elem.svg_path()

        result = ""
        if elem.rotation != 0:
            cx, cy = elem.center.x, elem.center.y
            result += f'  <g transform="rotate({elem.rotation}, {cx}, {cy})">\n'
            result += (
                f'    <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{elem.stroke_width}"/>\n'
            )
            result += "  </g>\n"
        else:
            result = (
                f'  <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{elem.stroke_width}"/>\n'
            )
        return result

    def _logic_gate_to_svg(self, gate) -> str:
        """Convert a logic gate to SVG markup."""
        fill_attr = self._get_color_attrs(gate.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(gate.stroke, "stroke", "black")
        path = gate.svg_path()

        result = ""
        if gate.rotation != 0:
            cx, cy = gate.center.x, gate.center.y
            result += f'  <g transform="rotate({gate.rotation}, {cx}, {cy})">\n'
            result += (
                f'    <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{gate.stroke_width}"/>\n'
            )
            if hasattr(gate, "get_pin_labels"):
                for label_text, pos, anchor in gate.get_pin_labels():
                    text_anchor = (
                        "start" if anchor == "start" else ("end" if anchor == "end" else "middle")
                    )
                    result += (
                        f'    <text x="{pos.x}" y="{pos.y}" '
                        f'text-anchor="{text_anchor}" dominant-baseline="middle" '
                        f'font-family="monospace" font-size="10" fill="black">'
                        f"{self._escape_xml(label_text)}</text>\n"
                    )
            result += "  </g>\n"
        else:
            result = (
                f'  <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{gate.stroke_width}"/>\n'
            )
            if hasattr(gate, "get_pin_labels"):
                for label_text, pos, anchor in gate.get_pin_labels():
                    text_anchor = (
                        "start" if anchor == "start" else ("end" if anchor == "end" else "middle")
                    )
                    result += (
                        f'  <text x="{pos.x}" y="{pos.y}" '
                        f'text-anchor="{text_anchor}" dominant-baseline="middle" '
                        f'font-family="monospace" font-size="10" fill="black">'
                        f"{self._escape_xml(label_text)}</text>\n"
                    )
        return result

    def _opamp_to_svg(self, opamp) -> str:
        """Convert an op-amp to SVG markup."""
        fill_attr = self._get_color_attrs(opamp.fill, "fill", "none")
        stroke_attr = self._get_color_attrs(opamp.stroke, "stroke", "black")
        path = opamp.svg_path()

        result = ""
        if opamp.rotation != 0:
            cx, cy = opamp.center.x, opamp.center.y
            result += f'  <g transform="rotate({opamp.rotation}, {cx}, {cy})">\n'
            result += (
                f'    <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{opamp.stroke_width}"/>\n'
            )
            for symbol, pos in opamp.svg_symbols():
                result += (
                    f'    <text x="{pos.x}" y="{pos.y}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'font-family="sans-serif" font-size="14" font-weight="bold" fill="black">'
                    f"{self._escape_xml(symbol)}</text>\n"
                )
            result += "  </g>\n"
        else:
            result = (
                f'  <path d="{path}" '
                f'{fill_attr} {stroke_attr} stroke-width="{opamp.stroke_width}"/>\n'
            )
            for symbol, pos in opamp.svg_symbols():
                result += (
                    f'  <text x="{pos.x}" y="{pos.y}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'font-family="sans-serif" font-size="14" font-weight="bold" fill="black">'
                    f"{self._escape_xml(symbol)}</text>\n"
                )
        return result

    def _circuit_wire_to_svg(self, wire) -> str:
        """Convert a wire or bus to SVG markup."""
        stroke_attr = self._get_color_attrs(wire.stroke, "stroke", "black")
        path = wire.svg_path()

        result = (
            f'  <path d="{path}" '
            f'fill="none" {stroke_attr} stroke-width="{wire.stroke_width}"/>\n'
        )

        if hasattr(wire, "show_slash") and wire.show_slash and hasattr(wire, "slash_position"):
            mid, angle = wire.slash_position
            import math

            slash_len = 8
            perp_angle = angle + math.pi / 4
            x1 = mid.x - math.cos(perp_angle) * slash_len / 2
            y1 = mid.y - math.sin(perp_angle) * slash_len / 2
            x2 = mid.x + math.cos(perp_angle) * slash_len / 2
            y2 = mid.y + math.sin(perp_angle) * slash_len / 2
            result += (
                f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'{stroke_attr} stroke-width="{wire.stroke_width}"/>\n'
            )
            if hasattr(wire, "bus_width"):
                result += (
                    f'  <text x="{mid.x + 5}" y="{mid.y - 5}" '
                    f'font-family="monospace" font-size="8" fill="black">'
                    f"{wire.bus_width}</text>\n"
                )

        return result

    def _wire_junction_to_svg(self, junction) -> str:
        """Convert a wire junction (dot) to SVG markup."""
        fill_attr = self._get_color_attrs(junction.fill, "fill", "black")
        stroke_attr = self._get_color_attrs(junction.stroke, "stroke", "none")
        cx, cy = junction.center.x, junction.center.y
        r = junction.radius
        return f'  <circle cx="{cx}" cy="{cy}" r="{r}" ' f"{fill_attr} {stroke_attr}/>\n"

    def _circuit_label_to_svg(self, label) -> str:
        """Convert a circuit label to SVG markup."""
        fill_attr = self._get_color_attrs(label.fill, "fill", "#707070")
        font_weight = getattr(label, "font_weight", "normal")
        return (
            f'  <text x="{label.position.x}" y="{label.position.y}" '
            f'text-anchor="{label.anchor}" dominant-baseline="middle" '
            f'font-family="{label.font_family}" font-size="{label.font_size}" '
            f'font-weight="{font_weight}" {fill_attr}>{self._escape_xml(label.text)}</text>\n'
        )

    def _image_to_svg(self, img: Image) -> str:
        """Convert an Image shape to SVG markup."""
        mime_type = img.get_mime_type()
        base64_data = img.get_base64_data()
        data_uri = f"data:{mime_type};base64,{base64_data}"

        opacity_attr = ""
        if img.opacity < 1.0:
            opacity_attr = f' opacity="{img.opacity}"'

        preserve = "xMidYMid meet" if img.preserve_aspect_ratio else "none"

        return (
            f'  <image x="{img.x}" y="{img.y}" '
            f'width="{img.width}" height="{img.height}" '
            f'href="{data_uri}" '
            f'preserveAspectRatio="{preserve}"{opacity_attr}/>\n'
        )
