"""
Base diagram class for OD-DO.

Provides the Diagram base class that all diagrams inherit from.
Diagrams contain shapes and can be nested within other diagrams.

Example:
    from od_do import diagram, shapes, colors

    class MyDiagram(diagram.Diagram):
        units = "um"
        unit_to_pixels = 40

        def draw(self):
            shapes.block(
                parent=self,
                ll=(100, 200),
                width=150,
                height=80,
                fill=colors.RED,
            )

    diag = MyDiagram()
    diag.render("output/diagram.svg")
"""

from __future__ import annotations

from typing import List, Optional, Union, TYPE_CHECKING

from ..shapes.base import Shape
from ..geometry import Point, BBox, PointLike, resolve_position

if TYPE_CHECKING:
    from ..placement import Placement
    from ..paths import Path


class Diagram:
    """Base class for all diagrams.

    Diagrams are containers for shapes, paths, and nested sub-diagrams.
    Override the `draw()` method to define your diagram's contents.

    Class Attributes (can be set at class level or passed to __init__):
        units: Unit system (e.g., "px", "mm", "um"). Default: "px"
        unit_to_pixels: Conversion ratio from units to pixels. Default: 1.0

    Constructor Parameters:
        parent: Parent diagram. If provided, this diagram becomes a sub-diagram
                and is automatically placed within the parent.
        ll, ul, lr, ur: Position when placed as a sub-diagram (specify one).
                        Defaults to ll=(0, 0) if none specified.
        rotation: Rotation in degrees when placed as a sub-diagram.
        mirror: Mirror type ("MX", "MY", or "MX_MY") when placed as a sub-diagram.
        rotation_offset: (x, y) tuple for custom rotation pivot point.
        width, height: Explicit dimensions or "auto" for auto-sizing based on content.
        units: Override class-level units setting.
        unit_to_pixels: Override class-level unit_to_pixels setting.

    Subclassing:
        Override the `draw()` method to define shapes and sub-diagrams.
        Do NOT override `__init__` unless you need custom constructor parameters.

    Example:
        class MyComponent(Diagram):
            units = "um"
            unit_to_pixels = 40

            def draw(self):
                shapes.block(parent=self, ll=(0, 50), width=100, height=50, fill="#3498db")
                shapes.circle(parent=self, center=(80, 25), radius=15, fill="#e74c3c")

        # Use it - no super().__init__() boilerplate needed!
        MyComponent(parent=main_diagram, ll=(100, 50), rotation=45)
    """

    # Class-level defaults (can be overridden in subclasses)
    units: str = "px"
    unit_to_pixels: float = 1.0

    def __init__(
        self,
        parent: Optional[Diagram] = None,
        ll: Optional[PointLike] = None,
        ul: Optional[PointLike] = None,
        lr: Optional[PointLike] = None,
        ur: Optional[PointLike] = None,
        rotation: float = 0,
        mirror: Optional[str] = None,
        rotation_offset: Optional[tuple] = None,
        width: Union[int, float, str] = "auto",
        height: Union[int, float, str] = "auto",
        units: Optional[str] = None,
        unit_to_pixels: Optional[float] = None,
        background: Optional[str] = None,
    ):
        """Create a diagram.

        Args:
            parent: Parent diagram for nesting.
            ll: Lower-left corner position when nested (Point or 2-tuple).
            ul: Upper-left corner position when nested (Point or 2-tuple).
            lr: Lower-right corner position when nested (Point or 2-tuple).
            ur: Upper-right corner position when nested (Point or 2-tuple).
            rotation: Rotation in degrees when nested.
            mirror: Mirror type when nested.
            rotation_offset: Custom rotation pivot point.
            width: Width or "auto" for auto-sizing.
            height: Height or "auto" for auto-sizing.
            units: Unit system (overrides class attribute).
            unit_to_pixels: Pixel conversion (overrides class attribute).
            background: Background color (hex string or Color).
        """
        self.parent = parent
        self.width = width
        self.height = height
        self.background = background

        # Resolve units: parameter > class attribute > parent > default
        if units is not None:
            self._units = units
        elif hasattr(self.__class__, "units") and self.__class__.units != Diagram.units:
            self._units = self.__class__.units
        elif parent is not None:
            self._units = parent._units
        else:
            self._units = "px"

        # Resolve unit_to_pixels: parameter > class attribute > parent > default
        if unit_to_pixels is not None:
            self._unit_to_pixels = unit_to_pixels
        elif (
            hasattr(self.__class__, "unit_to_pixels")
            and self.__class__.unit_to_pixels != Diagram.unit_to_pixels
        ):
            self._unit_to_pixels = self.__class__.unit_to_pixels
        elif parent is not None:
            self._unit_to_pixels = parent._unit_to_pixels
        else:
            self._unit_to_pixels = 1.0

        self.shapes: List[Union[Shape, "Placement", "Path"]] = []
        self._backend = None

        # Call draw() to let subclasses define their shapes
        self.draw()

        # Register with parent after draw() so all shapes exist
        if parent is not None:
            from ..placement import place as create_placement

            x, y = self._resolve_position(ll, ul, lr, ur)
            placement = create_placement(
                source=self,
                x=x,
                y=y,
                rotation=rotation,
                mirror=mirror,
                rotation_offset=rotation_offset,
            )
            parent.add_placement(placement)

    @property
    def units(self) -> str:
        """The unit system for this diagram."""
        return self._units

    @property
    def unit_to_pixels(self) -> float:
        """The conversion ratio from units to pixels."""
        return self._unit_to_pixels

    def _resolve_position(
        self,
        ll: Optional[PointLike],
        ul: Optional[PointLike],
        lr: Optional[PointLike],
        ur: Optional[PointLike],
    ) -> tuple:
        """Convert corner position to (x, y) offset for placement.

        Unlike shapes where (x, y) is the ul corner position, for diagram
        placements (x, y) is an offset. This calculates the offset needed
        to place the specified corner at the target position.
        """
        def to_tuple(p: PointLike) -> tuple:
            if isinstance(p, Point):
                return (p.x, p.y)
            return p

        specified = sum([ll is not None, ul is not None, lr is not None, ur is not None])

        if specified > 1:
            raise ValueError("Cannot specify multiple positioning modes (ll, ul, lr, ur)")

        if specified == 0:
            return (0, 0)

        bbox = self.bounding_box()
        min_x, min_y, max_x, max_y = bbox

        if ll is not None:
            target_x, target_y = to_tuple(ll)
            return (target_x - min_x, target_y - max_y)

        if ul is not None:
            target_x, target_y = to_tuple(ul)
            return (target_x - min_x, target_y - min_y)

        if lr is not None:
            target_x, target_y = to_tuple(lr)
            return (target_x - max_x, target_y - max_y)

        if ur is not None:
            target_x, target_y = to_tuple(ur)
            return (target_x - max_x, target_y - min_y)

        return (0, 0)

    def draw(self) -> None:
        """Override this method to define shapes and sub-diagrams.

        This method is called automatically by __init__ after the diagram
        is initialized but before it's registered with its parent.

        Example:
            def draw(self):
                shapes.block(parent=self, ll=(0, 100), width=100, height=50, fill="#3498db")
                shapes.circle(parent=self, center=(80, 25), radius=15, fill="#e74c3c")
        """
        pass

    def add_shape(self, shape: Union[Shape, "Path"]) -> None:
        """Add a shape or path to this diagram.

        Shapes typically auto-register themselves, so you rarely need to call this directly.
        """
        self.shapes.append(shape)

    def add_placement(self, placement: "Placement") -> None:
        """Add a placement (sub-diagram with transforms) to this diagram."""
        self.shapes.append(placement)

    @property
    def bbox(self) -> BBox:
        """Calculate the bounding box of all shapes in the diagram.

        Returns:
            BBox with ll (lower-left) and ur (upper-right) corners.
        """
        min_x, min_y, max_x, max_y = self.bounding_box()
        return BBox(
            ll=Point(min_x, max_y),
            ur=Point(max_x, min_y),
        )

    def bounding_box(self) -> tuple:
        """Calculate the bounding box of all shapes in the diagram.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) in user units.
        """
        from ..placement import Placement

        if not self.shapes:
            return (0, 0, 0, 0)

        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")

        for item in self.shapes:
            if isinstance(item, Placement):
                # Use the placement's rotated bounding box
                bbox = item.get_bounding_box()
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                max_x = max(max_x, bbox[2])
                max_y = max(max_y, bbox[3])
            else:
                bbox = item.bounding_box()
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                max_x = max(max_x, bbox[2])
                max_y = max(max_y, bbox[3])

        if min_x == float("inf"):
            return (0, 0, 0, 0)

        return (min_x, min_y, max_x, max_y)

    def _resolve_render_option(self, param_value, option_name, default):
        """Resolve a render option: explicit param > class attr > default."""
        if param_value is not ...:
            return param_value
        class_value = getattr(self, f"render_{option_name}", None)
        if class_value is not None:
            return class_value
        return default

    def render(
        self,
        output_path: str,
        backend: Optional[str] = ...,
        padding: float = ...,
        padding_left: Optional[float] = ...,
        padding_right: Optional[float] = ...,
        padding_top: Optional[float] = ...,
        padding_bottom: Optional[float] = ...,
        show: bool = ...,
        **kwargs,
    ) -> None:
        """Render the diagram to a file.

        Args:
            output_path: Path to write the output file.
            backend: Backend type ("svg", "png", "drawio"). Auto-detected from extension.
            padding: Default padding on all sides (in user units).
            padding_left: Override left padding.
            padding_right: Override right padding.
            padding_top: Override top padding.
            padding_bottom: Override bottom padding.
            show: Open the rendered file in the system viewer after saving.
            **kwargs: Additional backend-specific options.

        Render options can also be set as class attributes with the render_ prefix:
            render_padding, render_padding_left, render_backend, render_show, etc.
            Explicit parameters override class attributes.
        """
        import subprocess
        from .backends.svg import SVGBackend
        from .backends.png import PNGBackend
        from .backends.drawio import DrawIOBackend
        from ..config import get_config

        backend = self._resolve_render_option(backend, "backend", None)
        padding = self._resolve_render_option(padding, "padding", 50)
        padding_left = self._resolve_render_option(padding_left, "padding_left", None)
        padding_right = self._resolve_render_option(padding_right, "padding_right", None)
        padding_top = self._resolve_render_option(padding_top, "padding_top", None)
        padding_bottom = self._resolve_render_option(padding_bottom, "padding_bottom", None)
        show = self._resolve_render_option(show, "show", False)

        if backend == "svg" or output_path.endswith(".svg"):
            self._backend = SVGBackend()
        elif backend == "png" or output_path.endswith(".png"):
            self._backend = PNGBackend()
        elif backend == "drawio" or output_path.endswith(".drawio"):
            self._backend = DrawIOBackend()
        elif self._backend is None:
            self._backend = SVGBackend()

        # Resolve padding values
        pad_left = padding_left if padding_left is not None else padding
        pad_right = padding_right if padding_right is not None else padding
        pad_top = padding_top if padding_top is not None else padding
        pad_bottom = padding_bottom if padding_bottom is not None else padding

        # Calculate dimensions
        if self.width == "auto" or self.height == "auto":
            bbox = self.bounding_box()
            content_width = bbox[2] - bbox[0]
            content_height = bbox[3] - bbox[1]

        if self.width == "auto":
            width = (content_width + pad_left + pad_right) * self._unit_to_pixels
        else:
            width = self.width * self._unit_to_pixels

        if self.height == "auto":
            height = (content_height + pad_top + pad_bottom) * self._unit_to_pixels
        else:
            height = self.height * self._unit_to_pixels

        render_kwargs = {
            "width": width,
            "height": height,
            "unit_to_pixels": self._unit_to_pixels,
            "padding_left": pad_left,
            "padding_top": pad_top,
            "units": self._units,
            "background": self.background,
            **kwargs,
        }

        self._backend.render(self.shapes, output_path, **render_kwargs)

        if show:
            config = get_config()
            if output_path.endswith(".svg"):
                viewer = config["svg_viewer"]
            elif output_path.endswith(".png"):
                viewer = config["png_viewer"]
            else:
                viewer = config["svg_viewer"]
            subprocess.run([viewer, output_path])
