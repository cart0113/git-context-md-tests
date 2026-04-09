"""
Placement module for OD-DO.

Handles placing diagrams or shape groups within other diagrams
with position offset, rotation, and mirroring transformations.
"""

from typing import List, Optional, Union, TYPE_CHECKING
from .transform import Transform, Mirror
from .shapes.base import Shape

if TYPE_CHECKING:
    from .diagram.base import Diagram


class Placement:
    """
    Represents the placement of a diagram or shape group within another diagram.

    A Placement wraps a source (either a Diagram or a list of Shapes) and defines
    how to position and transform it when placed in a parent diagram.

    Transform Order:
    1. First, the source is translated to the (x, y) offset position
    2. If rotation_offset is given, the rotation pivot point is at (x + rotation_offset_x, y + rotation_offset_y)
    3. If rotation_offset is NOT given, the rotation pivot point is at (x, y) - the placement origin
    4. Rotation and mirroring are applied around the pivot point

    Example:
        If offset is (10, 20), rotation_offset is (100, 100), and rotation is 180:
        1. Shape is placed at (10, 20)
        2. Rotation pivot is at (10 + 100, 20 + 100) = (110, 120)
        3. Shape rotates 180 degrees around point (110, 120)

    Attributes:
        source: The Diagram or list of Shapes to place
        x: X offset position in parent diagram
        y: Y offset position in parent diagram
        transform: Rotation and mirror transformation to apply
        rotation_offset_x: X offset from (x, y) for rotation pivot point
        rotation_offset_y: Y offset from (x, y) for rotation pivot point
    """

    def __init__(
        self,
        source: Union["Diagram", List[Shape]],
        x: float = 0,
        y: float = 0,
        transform: Optional[Transform] = None,
        rotation_offset_x: Optional[float] = None,
        rotation_offset_y: Optional[float] = None,
    ):
        self.source = source
        self.x = x
        self.y = y
        self.transform = transform or Transform()
        self.rotation_offset_x = rotation_offset_x
        self.rotation_offset_y = rotation_offset_y

    @classmethod
    def create(
        cls,
        source: Union["Diagram", List[Shape]],
        x: float = 0,
        y: float = 0,
        rotation: float = 0,
        mirror: Optional[str] = None,
        rotation_offset: Optional[tuple] = None,
    ) -> "Placement":
        """
        Convenience factory method with simplified parameters.

        Args:
            source: The Diagram or list of Shapes to place
            x: X offset position
            y: Y offset position
            rotation: Rotation in degrees (0-360)
            mirror: Mirror type as string: "MX", "MY", or "MX_MY"
            rotation_offset: Tuple (x, y) offset from placement origin for rotation pivot

        Returns:
            Placement instance
        """
        # Parse mirror string
        mirror_enum = Mirror.NONE
        if mirror:
            mirror_upper = mirror.upper()
            if "MX" in mirror_upper and "MY" in mirror_upper:
                mirror_enum = Mirror.MXY
            elif "MX" in mirror_upper:
                mirror_enum = Mirror.MX
            elif "MY" in mirror_upper:
                mirror_enum = Mirror.MY

        transform = Transform(rotation=rotation, mirror=mirror_enum)

        rotation_offset_x = None
        rotation_offset_y = None
        if rotation_offset:
            rotation_offset_x = rotation_offset[0]
            rotation_offset_y = rotation_offset[1]

        return cls(
            source=source,
            x=x,
            y=y,
            transform=transform,
            rotation_offset_x=rotation_offset_x,
            rotation_offset_y=rotation_offset_y,
        )

    def get_shapes(self) -> List[Shape]:
        """Get the shapes from the source."""
        from .diagram.base import Diagram

        if isinstance(self.source, Diagram):
            return self.source.shapes
        return self.source

    def get_bounding_box(self) -> tuple:
        """
        Calculate the axis-aligned bounding box after applying transforms.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) accounting for rotation.
        """
        import math
        from .diagram.base import Diagram

        # Get the source's bounding box
        if isinstance(self.source, Diagram):
            src_bbox = self.source.bounding_box()
        else:
            # List of shapes - calculate bbox
            min_x = min_y = float("inf")
            max_x = max_y = float("-inf")
            for shape in self.source:
                bbox = shape.bounding_box()
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                max_x = max(max_x, bbox[2])
                max_y = max(max_y, bbox[3])
            src_bbox = (min_x, min_y, max_x, max_y)

        if src_bbox == (float("inf"), float("inf"), float("-inf"), float("-inf")):
            return (self.x, self.y, self.x, self.y)

        # Get the four corners of the source bbox
        corners = [
            (src_bbox[0], src_bbox[1]),  # min_x, min_y
            (src_bbox[2], src_bbox[1]),  # max_x, min_y
            (src_bbox[2], src_bbox[3]),  # max_x, max_y
            (src_bbox[0], src_bbox[3]),  # min_x, max_y
        ]

        # Apply rotation if any
        rotation = self.transform.rotation if self.transform else 0
        if rotation != 0:
            # Rotation is around (0, 0) in the local coordinate system
            angle_rad = math.radians(rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            rotated_corners = []
            for cx, cy in corners:
                # Rotate around origin
                rx = cx * cos_a - cy * sin_a
                ry = cx * sin_a + cy * cos_a
                rotated_corners.append((rx, ry))
            corners = rotated_corners

        # Translate corners by placement offset
        translated_corners = [(cx + self.x, cy + self.y) for cx, cy in corners]

        # Calculate axis-aligned bounding box
        xs = [c[0] for c in translated_corners]
        ys = [c[1] for c in translated_corners]

        return (min(xs), min(ys), max(xs), max(ys))

    def get_rotation_pivot(self) -> tuple:
        """
        Calculate the rotation pivot point.

        If rotation_offset is set, pivot is at (x + rotation_offset_x, y + rotation_offset_y)
        Otherwise, pivot is at (x, y) - the placement origin
        """
        if self.rotation_offset_x is not None and self.rotation_offset_y is not None:
            return (self.x + self.rotation_offset_x, self.y + self.rotation_offset_y)
        return (self.x, self.y)

    def to_svg_group(self) -> str:
        """
        Generate SVG <g> element with transforms for this placement.

        The group will contain the translated and transformed shapes.
        """
        from .diagram.backends.svg import SVGBackend

        backend = SVGBackend()

        # Calculate transforms
        transforms = []

        # Step 1: Translate to position
        if self.x != 0 or self.y != 0:
            transforms.append(f"translate({self.x}, {self.y})")

        # Step 2 & 3: Apply rotation/mirror around pivot point
        if not self.transform.is_identity():
            # Calculate pivot relative to the translated position
            if self.rotation_offset_x is not None and self.rotation_offset_y is not None:
                pivot_x = self.rotation_offset_x
                pivot_y = self.rotation_offset_y
            else:
                pivot_x = 0
                pivot_y = 0

            # Generate transform string
            transform_str = self.transform.to_svg_transform(pivot_x, pivot_y)
            if transform_str:
                transforms.append(transform_str)

        transform_attr = ""
        if transforms:
            transform_attr = f' transform="{" ".join(transforms)}"'

        # Generate shape content
        shapes_svg = ""
        for shape in self.get_shapes():
            shapes_svg += backend._shape_to_svg(shape)

        return f"  <g{transform_attr}>\n{shapes_svg}  </g>\n"

    @property
    def has_transform(self) -> bool:
        """Check if this placement has any non-identity transform."""
        return self.x != 0 or self.y != 0 or not self.transform.is_identity()

    def __repr__(self):
        parts = [f"Placement(x={self.x}, y={self.y}"]
        if not self.transform.is_identity():
            parts.append(f", transform={self.transform}")
        if self.rotation_offset_x is not None:
            parts.append(f", rotation_offset=({self.rotation_offset_x}, {self.rotation_offset_y})")
        parts.append(")")
        return "".join(parts)


def place(
    source: Union["Diagram", List[Shape]],
    x: float = 0,
    y: float = 0,
    rotation: float = 0,
    mirror: Optional[str] = None,
    rotation_offset: Optional[tuple] = None,
) -> Placement:
    """
    Convenience function to create a Placement.

    Args:
        source: The Diagram or list of Shapes to place
        x: X offset position
        y: Y offset position
        rotation: Rotation in degrees (0-360)
        mirror: Mirror type as string: "MX", "MY", or "MX_MY"
        rotation_offset: Tuple (x, y) offset from placement origin for rotation pivot

    Returns:
        Placement instance

    Example:
        # Place a sub-diagram at position (100, 200) rotated 90 degrees
        placed = place(my_subdiagram, x=100, y=200, rotation=90)

        # Place with rotation around an offset point
        placed = place(my_subdiagram, x=10, y=20, rotation=180, rotation_offset=(100, 100))
        # This places at (10, 20), then rotates 180° around (110, 120)
    """
    return Placement.create(
        source=source,
        x=x,
        y=y,
        rotation=rotation,
        mirror=mirror,
        rotation_offset=rotation_offset,
    )
