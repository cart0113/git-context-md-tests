"""
Transform module for OD-DO.

Handles rotation (R0-R360) and mirroring (MX, MY) transformations.
"""

from enum import Enum
from typing import Optional


class Mirror(Enum):
    """Mirror transformation types."""

    NONE = "none"
    MX = "mx"  # Mirror across X axis (flip vertically)
    MY = "my"  # Mirror across Y axis (flip horizontally)
    MXY = "mxy"  # Mirror across both axes


class Transform:
    """
    Represents a transformation consisting of rotation and/or mirroring.

    Rotation is specified in degrees (0-360).
    Mirroring can be MX (mirror X - flip vertically), MY (mirror Y - flip horizontally),
    or MXY (both).

    Transform order when applied:
    1. Mirror operations are applied first
    2. Rotation is applied second
    """

    def __init__(
        self,
        rotation: float = 0,
        mirror: Mirror = Mirror.NONE,
    ):
        self.rotation = self._normalize_rotation(rotation)
        self.mirror = mirror

    def _normalize_rotation(self, rotation: float) -> float:
        """Normalize rotation to 0-360 range."""
        rotation = rotation % 360
        if rotation < 0:
            rotation += 360
        return rotation

    @classmethod
    def from_string(cls, transform_str: str) -> "Transform":
        """
        Parse a transform string like "R90", "MX", "MY", "R180_MX", etc.

        Format:
        - R{degrees} for rotation (e.g., R90, R180, R270, R45)
        - MX for mirror X (flip vertically)
        - MY for mirror Y (flip horizontally)
        - Can combine with underscore: R90_MX, R180_MY, MX_MY
        """
        rotation = 0
        mirror = Mirror.NONE
        has_mx = False
        has_my = False

        parts = transform_str.upper().split("_")

        for part in parts:
            if part.startswith("R"):
                rotation = float(part[1:])
            elif part == "MX":
                has_mx = True
            elif part == "MY":
                has_my = True

        if has_mx and has_my:
            mirror = Mirror.MXY
        elif has_mx:
            mirror = Mirror.MX
        elif has_my:
            mirror = Mirror.MY

        return cls(rotation=rotation, mirror=mirror)

    def to_string(self) -> str:
        """Convert transform to string representation."""
        parts = []

        if self.rotation != 0:
            if self.rotation == int(self.rotation):
                parts.append(f"R{int(self.rotation)}")
            else:
                parts.append(f"R{self.rotation}")

        if self.mirror == Mirror.MX:
            parts.append("MX")
        elif self.mirror == Mirror.MY:
            parts.append("MY")
        elif self.mirror == Mirror.MXY:
            parts.append("MX")
            parts.append("MY")

        return "_".join(parts) if parts else "R0"

    def to_svg_transform(
        self,
        center_x: float,
        center_y: float,
    ) -> str:
        """
        Generate SVG transform attribute value.

        Args:
            center_x: X coordinate of the transform center point
            center_y: Y coordinate of the transform center point

        Returns:
            SVG transform string (e.g., "rotate(90 100 100) scale(-1, 1)")
        """
        transforms = []

        # Apply mirror first (scale transform)
        if self.mirror == Mirror.MX:
            # Mirror across X axis = flip vertically = scale(1, -1)
            # Need to translate to center, scale, translate back
            transforms.append(f"translate({center_x}, {center_y})")
            transforms.append("scale(1, -1)")
            transforms.append(f"translate({-center_x}, {-center_y})")
        elif self.mirror == Mirror.MY:
            # Mirror across Y axis = flip horizontally = scale(-1, 1)
            transforms.append(f"translate({center_x}, {center_y})")
            transforms.append("scale(-1, 1)")
            transforms.append(f"translate({-center_x}, {-center_y})")
        elif self.mirror == Mirror.MXY:
            # Mirror both = scale(-1, -1)
            transforms.append(f"translate({center_x}, {center_y})")
            transforms.append("scale(-1, -1)")
            transforms.append(f"translate({-center_x}, {-center_y})")

        # Apply rotation second
        if self.rotation != 0:
            transforms.append(f"rotate({self.rotation} {center_x} {center_y})")

        return " ".join(transforms)

    def is_identity(self) -> bool:
        """Check if this transform is the identity (no-op)."""
        return self.rotation == 0 and self.mirror == Mirror.NONE

    def __repr__(self):
        return f"Transform({self.to_string()})"

    def __eq__(self, other):
        if not isinstance(other, Transform):
            return False
        return self.rotation == other.rotation and self.mirror == other.mirror


# Convenience constants for common transforms
R0 = Transform(rotation=0)
R90 = Transform(rotation=90)
R180 = Transform(rotation=180)
R270 = Transform(rotation=270)
MX = Transform(mirror=Mirror.MX)
MY = Transform(mirror=Mirror.MY)
MXY = Transform(mirror=Mirror.MXY)
