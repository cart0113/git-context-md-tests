"""
Geometry class for Draw.io object dimensions and positioning.

Adapted from drawpyo/diagram/base_diagram.py (Geometry class)
Source: https://github.com/MerrimanInd/drawpyo
Original Author: Merrimanind
License: MIT

This module provides the Geometry class which represents the size and
position of Draw.io diagram objects.
"""

from typing import Any, Optional, TYPE_CHECKING

from .xml_base import XMLBase

if TYPE_CHECKING:
    from .object import Object


class Geometry(XMLBase):
    """
    Represents the geometry (position and size) of a Draw.io object.

    In Draw.io's XML format, geometry is represented as a nested
    <mxGeometry> element within an object.

    Adapted from drawpyo.diagram.base_diagram.Geometry
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize geometry for a diagram object.

        Args:
            parent_object: The object this geometry belongs to
            x: X coordinate
            y: Y coordinate
            width: Object width
            height: Object height
            as_attribute: XML attribute name (default: "geometry")
        """
        super().__init__(**kwargs)
        self.xml_class: str = "mxGeometry"

        self.parent_object: Optional["Object"] = kwargs.get("parent_object", None)
        self.x: float = kwargs.get("x", 0)
        self.y: float = kwargs.get("y", 0)
        self.width: float = kwargs.get("width", 120)
        self.height: float = kwargs.get("height", 60)
        self.as_attribute: str = kwargs.get("as_attribute", "geometry")

    @property
    def attributes(self) -> dict[str, Any]:
        """
        XML attributes for the geometry element.

        Returns:
            Dictionary of geometry attributes
        """
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "as": self.as_attribute,
        }

    @property
    def size(self) -> tuple[float, float]:
        """
        Get size as a tuple.

        Returns:
            Tuple of (width, height)
        """
        return (self.width, self.height)

    @size.setter
    def size(self, value: tuple[float, float]) -> None:
        """
        Set size from a tuple.

        Args:
            value: Tuple of (width, height)
        """
        self.width = value[0]
        self.height = value[1]
