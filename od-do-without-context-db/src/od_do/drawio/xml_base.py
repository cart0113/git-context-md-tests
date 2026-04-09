"""
Base XML generation functionality.

Adapted from drawpyo/xml_base.py
Source: https://github.com/MerrimanInd/drawpyo
Original Author: Merrimanind
License: MIT (drawpyo is open source)

This module provides the base class for all Draw.io XML objects, handling
XML tag generation and character escaping.
"""

from typing import Any, Optional

# XML character escape mappings
# Copied from drawpyo/xml_base.py
XML_ESCAPE_MAP = {
    ">": "&gt;",
    "<": "&lt;",
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
}


class XMLBase:
    """
    Base class for all Draw.io XML objects.

    This class provides XML generation functionality that all Draw.io objects
    inherit from. It handles creating XML opening/closing tags with attributes
    and proper character escaping.

    Adapted from drawpyo.xml_base.XMLBase
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize XML base object.

        Args:
            id: Unique identifier for the object (defaults to Python id())
            xml_class: XML tag name for this object
            xml_parent: Parent object ID for nested structures
            tag: Optional tag attribute for grouping/filtering in Draw.io
        """
        self._id: int = kwargs.get("id", id(self))
        self.xml_class: str = kwargs.get("xml_class", "xml_tag")
        self.xml_parent: Optional[int] = kwargs.get("xml_parent", None)
        self.tag: Optional[str] = kwargs.get("tag", None)

    @property
    def id(self) -> int:
        """
        Unique identifier for this object.

        Draw.io uses unique IDs to reference objects. We use Python's id()
        function which guarantees unique identifiers within a session.

        Returns:
            Unique integer identifier
        """
        return self._id

    @property
    def attributes(self) -> dict[str, Any]:
        """
        XML attributes for this object.

        Subclasses override this to provide their specific attributes.

        Returns:
            Dictionary of attribute names to values
        """
        return {"id": self.id, "parent": self.xml_parent}

    @property
    def xml_open_tag(self) -> str:
        """
        Generate opening XML tag with attributes.

        Creates a tag like: <className attr1="value1" attr2="value2">

        Adapted from drawpyo.xml_base.XMLBase.xml_open_tag

        Returns:
            Opening XML tag string
        """
        if self.tag:
            # Handle UserObject tags for filtering/grouping
            open_user_object_tag = (
                f'<UserObject label="{getattr(self, "value", "")}" '
                f'tags="{self.tag}" id="{self.id}">'
            )
            open_tag = f"<{self.xml_class}"
            for attr_name, attr_value in self.attributes.items():
                if attr_name in ("id", "value"):
                    continue
                if attr_value is not None:
                    xml_param = self._xml_escape(str(attr_value))
                    open_tag += f' {attr_name}="{xml_param}"'
            return open_user_object_tag + "\n" + open_tag + ">"

        # Standard tag without UserObject wrapper
        open_tag = f"<{self.xml_class}"
        for attr_name, attr_value in self.attributes.items():
            if attr_value is not None:
                xml_param = self._xml_escape(str(attr_value))
                open_tag += f' {attr_name}="{xml_param}"'
        return open_tag + ">"

    @property
    def xml_close_tag(self) -> str:
        """
        Generate closing XML tag.

        Creates a tag like: </className>

        Returns:
            Closing XML tag string
        """
        if self.tag:
            return f"</{self.xml_class}>\n</UserObject>"
        return f"</{self.xml_class}>"

    @property
    def xml(self) -> str:
        """
        Generate complete XML for this object.

        Default implementation creates a self-closing tag.
        Subclasses with nested content override this.

        Returns:
            Complete XML string for this object
        """
        return self.xml_open_tag[:-1] + " />"

    def _xml_escape(self, text: str) -> str:
        """
        Escape special XML characters in text.

        Adapted from drawpyo.xml_base.XMLBase.xml_ify

        Args:
            text: String to escape

        Returns:
            String with XML special characters escaped
        """
        result = ""
        for char in text:
            if char in XML_ESCAPE_MAP:
                result += XML_ESCAPE_MAP[char]
            else:
                result += char
        return result
