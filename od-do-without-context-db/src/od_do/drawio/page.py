"""
Draw.io Page class and related XML structures.

Adapted from drawpyo/page.py
Source: https://github.com/MerrimanInd/drawpyo
Original Author: Merrimanind
License: MIT

This module provides the Page class which represents a page in a Draw.io
document, along with the nested XML structures (Diagram, mxGraph, Root).
"""

from typing import Any, Optional, TYPE_CHECKING

from .xml_base import XMLBase

if TYPE_CHECKING:
    from .file import File


class Page:
    """
    Represents a page in a Draw.io document.

    A page contains diagram objects and formatting attributes. Each Draw.io
    file has one or more pages. In the XML format, a page consists of three
    nested tags: Diagram, mxGraphModel, and root.

    Adapted from drawpyo.page.Page
    """

    def __init__(self, file: Optional["File"] = None, **kwargs: Any) -> None:
        """
        Initialize a Draw.io page.

        Args:
            file: Parent File object (optional)
            **kwargs: Page properties (name, dimensions, grid settings, etc.)
        """
        super().__init__()
        self.id: int = id(self)
        self.file: Optional["File"] = file
        self.objects: list[XMLBase] = kwargs.get("objects", [])

        # Every Draw.io diagram has two empty top-level mxCell objects
        # These are required by the Draw.io format
        # Copied from drawpyo/page.py
        self.objects.append(XMLBase(id=0, xml_class="mxCell"))
        self.objects.append(XMLBase(id=1, xml_class="mxCell", xml_parent=0))

        # Page properties
        if self.file is not None:
            page_num = len(self.file.pages)
        else:
            page_num = 1

        self.name: str = kwargs.get("name", f"Page-{page_num}")
        self.page_num: int = kwargs.get("page_num", page_num)

        # Page formatting properties (from Draw.io spec)
        # Copied from drawpyo/page.py
        self.dx: int = kwargs.get("dx", 2037)
        self.dy: int = kwargs.get("dy", 830)
        self.grid: int = kwargs.get("grid", 1)
        self.grid_size: int = kwargs.get("grid_size", 10)
        self.guides: int = kwargs.get("guides", 1)
        self.tooltips: int = kwargs.get("tooltips", 1)
        self.connect: int = kwargs.get("connect", 1)
        self.arrows: int = kwargs.get("arrows", 1)
        self.fold: int = kwargs.get("fold", 1)
        self.scale: int = kwargs.get("scale", 1)
        self.width: int = kwargs.get("width", 850)
        self.height: int = kwargs.get("height", 1100)
        self.math: int = kwargs.get("math", 0)
        self.shadow: int = kwargs.get("shadow", 0)

        # Nested XML structures required by Draw.io format
        # Adapted from drawpyo/page.py
        self.diagram = Diagram(name=self.name)
        self.mxGraph = MxGraph(page=self)
        self.root = Root()

    def __repr__(self) -> str:
        return f"Draw.io Page - {self.name}"

    def remove(self) -> None:
        """
        Remove this page from its parent file and delete it.
        """
        if self.file is not None:
            self.file.remove_page(self)
        del self

    def add_object(self, obj: XMLBase) -> None:
        """
        Add a diagram object to this page.

        Args:
            obj: Object to add to the page
        """
        if obj not in self.objects:
            self.objects.append(obj)

    def remove_object(self, obj: XMLBase) -> None:
        """
        Remove a diagram object from this page.

        Args:
            obj: Object to remove
        """
        self.objects.remove(obj)

    @property
    def file(self) -> Optional["File"]:
        """
        Parent file containing this page.

        Returns:
            File object or None
        """
        return self._file

    @file.setter
    def file(self, f: Optional["File"]) -> None:
        """
        Set the parent file and add this page to it.

        Args:
            f: File object or None
        """
        if f is not None:
            f.add_page(self)
        self._file = f

    @file.deleter
    def file(self) -> None:
        """
        Remove this page from its parent file.
        """
        if self._file is not None:
            self._file.remove_page(self)
        self._file = None

    @property
    def xml(self) -> str:
        """
        Generate complete XML for this page.

        Combines all objects within the nested Diagram/mxGraph/root structure.

        Adapted from drawpyo.page.Page.xml

        Returns:
            Complete page XML string
        """
        xml_string = self.xml_open_tag
        for obj in self.objects:
            xml_string += "\n        " + obj.xml
        xml_string += "\n" + self.xml_close_tag
        return xml_string

    @property
    def xml_open_tag(self) -> str:
        """
        Generate opening tags for the page's nested structure.

        Returns:
            Opening XML tags string
        """
        tag = (
            self.diagram.xml_open_tag
            + "\n    "
            + self.mxGraph.xml_open_tag
            + "\n      "
            + self.root.xml_open_tag
        )
        return tag

    @property
    def xml_close_tag(self) -> str:
        """
        Generate closing tags for the page's nested structure.

        Returns:
            Closing XML tags string
        """
        tag = (
            "      "
            + self.root.xml_close_tag
            + "\n    "
            + self.mxGraph.xml_close_tag
            + "\n  "
            + self.diagram.xml_close_tag
        )
        return tag


class Diagram(XMLBase):
    """
    Diagram XML element (outermost page element).

    Adapted from drawpyo.page.Diagram
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name: str = kwargs.get("name", "")
        self.xml_class: str = "diagram"

    @property
    def attributes(self) -> dict[str, Any]:
        return {"name": self.name, "id": self.id}


class MxGraph(XMLBase):
    """
    mxGraphModel XML element (middle page element).

    Contains grid, guides, and page formatting attributes.

    Adapted from drawpyo.page.mxGraph
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "mxGraphModel"
        self.page: Optional[Page] = kwargs.get("page", None)

    @property
    def attributes(self) -> dict[str, Any]:
        """
        XML attributes from the parent page's properties.

        Returns:
            Dictionary of mxGraphModel attributes
        """
        if self.page is None:
            return {}

        return {
            "dx": self.page.dx,
            "dy": self.page.dy,
            "grid": self.page.grid,
            "gridSize": self.page.grid_size,
            "guides": self.page.guides,
            "toolTips": self.page.tooltips,
            "connect": self.page.connect,
            "arrows": self.page.arrows,
            "fold": self.page.fold,
            "page": self.page.page_num,
            "pageScale": self.page.scale,
            "pageWidth": self.page.width,
            "pageHeight": self.page.height,
            "math": self.page.math,
            "shadow": self.page.shadow,
        }


class Root(XMLBase):
    """
    Root XML element (innermost page element, contains objects).

    Adapted from drawpyo.page.Root
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "root"

    @property
    def attributes(self) -> dict[str, Any]:
        return {}
