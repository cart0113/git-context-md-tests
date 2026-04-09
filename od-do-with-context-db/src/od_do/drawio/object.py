"""
Draw.io Object class for diagram shapes.

Adapted from drawpyo/diagram/objects.py and drawpyo/diagram/base_diagram.py
Source: https://github.com/MerrimanInd/drawpyo
Original Author: Merrimanind
License: MIT

This module provides the Object class which represents shapes and other
diagram elements in Draw.io. We've simplified it to focus only on basic
shapes needed for od-do.
"""

from typing import Any, Optional, TYPE_CHECKING

from .xml_base import XMLBase
from .geometry import Geometry

if TYPE_CHECKING:
    from .page import Page


def style_str_from_dict(style_dict: dict[str, Any]) -> str:
    """
    Convert a style dictionary to a Draw.io style string.

    Draw.io style format: baseStyle;attr1=value;attr2=value

    Adapted from drawpyo.diagram.base_diagram.style_str_from_dict

    Args:
        style_dict: Dictionary of style attributes

    Returns:
        Formatted style string
    """
    if "baseStyle" in style_dict:
        style_str = [style_dict.pop("baseStyle")]
    else:
        style_str = []

    style_str.extend(
        f"{attr}={value}" for attr, value in style_dict.items() if value not in ("", None)
    )

    return ";".join(style_str)


class Object(XMLBase):
    """
    Represents a shape or diagram element in Draw.io.

    Objects can be rectangles, ellipses, or any other Draw.io shape.
    They have geometry (position/size), styling, and optional text content.

    Adapted from drawpyo.diagram.objects.Object
    Simplified to remove edges, groups, containers, and other advanced features.
    """

    def __init__(
        self,
        page: Optional["Page"] = None,
        value: str = "",
        shape: str = "rectangle",
        **kwargs: Any,
    ) -> None:
        """
        Initialize a Draw.io object.

        Args:
            page: Page to add this object to
            value: Text content of the object
            shape: Shape type (rectangle, ellipse, etc.)
            **kwargs: Additional properties (see below)

        Keyword Args:
            position: (x, y) tuple for object position
            width: Object width in pixels
            height: Object height in pixels
            fillColor: Fill color as hex string (#RRGGBB)
            strokeColor: Stroke color as hex string (#RRGGBB)
            strokeWidth: Stroke width in pixels
            rounded: Whether to round corners (0 or 1)
            whiteSpace: Text wrapping mode (default: "wrap")
        """
        super().__init__(**kwargs)

        self.xml_class: str = "mxCell"
        self.page: Optional["Page"] = page
        self.value: str = value
        self.shape: str = shape

        # Geometry
        self.geometry: Geometry = Geometry(parent_object=self)
        position = kwargs.get("position", (0, 0))
        self.geometry.x = position[0]
        self.geometry.y = position[1]
        self.geometry.width = kwargs.get("width", 120)
        self.geometry.height = kwargs.get("height", 80)

        # Vertex flag (1 for shapes, 0 for edges)
        self.vertex: int = kwargs.get("vertex", 1)

        # Style attributes
        # Based on drawpyo.diagram.objects.Object style handling
        self.baseStyle: Optional[str] = kwargs.get("baseStyle", None)
        self.rounded: int = kwargs.get("rounded", 0)
        self.whiteSpace: str = kwargs.get("whiteSpace", "wrap")
        self.fillColor: Optional[str] = kwargs.get("fillColor", None)
        self.strokeColor: Optional[str] = kwargs.get("strokeColor", None)
        self.strokeWidth: Optional[int] = kwargs.get("strokeWidth", None)

        # Add to page if provided
        if page is not None:
            page.add_object(self)

    def __repr__(self) -> str:
        if self.value:
            return f"Draw.io Object ({self.shape}): {self.value}"
        return f"Draw.io Object ({self.shape})"

    @property
    def attributes(self) -> dict[str, Any]:
        """
        XML attributes for the object element.

        Adapted from drawpyo.diagram.objects.Object.attributes

        Returns:
            Dictionary of mxCell attributes
        """
        return {
            "id": self.id,
            "value": self.value,
            "style": self.style,
            "vertex": self.vertex,
            "parent": self.xml_parent_id,
        }

    @property
    def xml_parent_id(self) -> int:
        """
        Parent ID for this object in the XML hierarchy.

        Objects are children of the page root (ID=1).

        Returns:
            Parent object ID
        """
        return 1

    @property
    def style(self) -> str:
        """
        Generate Draw.io style string from object properties.

        Combines shape, colors, dimensions, and other styling into
        the Draw.io style format.

        Adapted from drawpyo.diagram.base_diagram.DiagramBase.style

        Returns:
            Formatted style string
        """
        style_dict: dict[str, Any] = {}

        # Base style
        if self.baseStyle:
            style_dict["baseStyle"] = self.baseStyle

        # Shape is usually included in the style string
        # unless it's the default rectangle
        if self.shape and self.shape != "rectangle":
            style_dict["shape"] = self.shape

        # Add non-None style attributes
        if self.rounded is not None:
            style_dict["rounded"] = self.rounded
        if self.whiteSpace is not None:
            style_dict["whiteSpace"] = self.whiteSpace
        if self.fillColor is not None:
            style_dict["fillColor"] = self.fillColor
        if self.strokeColor is not None:
            style_dict["strokeColor"] = self.strokeColor
        if self.strokeWidth is not None:
            style_dict["strokeWidth"] = self.strokeWidth

        return style_str_from_dict(style_dict)

    @property
    def xml(self) -> str:
        """
        Generate complete XML for this object.

        Objects contain a nested geometry element.

        Adapted from drawpyo.diagram.objects.Object.xml

        Returns:
            Complete object XML string
        """
        tag = self.xml_open_tag + "\n  " + self.geometry.xml + "\n" + self.xml_close_tag
        return tag
