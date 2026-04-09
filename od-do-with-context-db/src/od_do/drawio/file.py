"""
Draw.io File class for managing diagram files.

Adapted from drawpyo/file.py
Source: https://github.com/MerrimanInd/drawpyo
Original Author: Merrimanind
License: MIT

This module provides the File class which represents a Draw.io file
and handles writing it to disk.
"""

from datetime import datetime
from os import path, makedirs
from sys import version_info
from typing import Any, Optional

from .xml_base import XMLBase
from .page import Page


class File(XMLBase):
    """
    Represents a Draw.io file with its pages and metadata.

    A Draw.io file contains one or more pages, each with diagram objects.
    This class manages the file-level properties and writing to disk.

    Adapted from drawpyo.file.File
    """

    def __init__(
        self,
        file_name: str = "Diagram.drawio",
        file_path: str = path.join(path.expanduser("~"), "Diagrams"),
    ) -> None:
        """
        Initialize a Draw.io file.

        Args:
            file_name: Name of the file to create
            file_path: Directory path where file will be saved
        """
        super().__init__()

        self.pages: list[Page] = []
        self.file_name: str = file_name
        self.file_path: str = file_path

        # Draw.io file format attributes
        # These values are based on the Draw.io specification
        self.host: str = "od-do"
        self.type: str = "device"
        self.version: str = "21.6.5"  # Draw.io spec version
        self.xml_class: str = "mxfile"

    def __repr__(self) -> str:
        return f"Draw.io File - {self.file_name}"

    @property
    def attributes(self) -> dict[str, Any]:
        """
        XML attributes for the file element.

        Returns:
            Dictionary of file-level XML attributes
        """
        return {
            "host": self.host,
            "modified": self.modified,
            "agent": self.agent,
            "etag": self.etag,
            "version": self.version,
            "type": self.type,
        }

    def add_page(self, page: Page) -> None:
        """
        Add a page to this file.

        Args:
            page: Page object to add
        """
        page._file = self
        self.pages.append(page)

    def remove_page(self, page: Page | str | int) -> None:
        """
        Remove a page from the file.

        Args:
            page: Page object, page name (str), or page index (int)
        """
        if isinstance(page, int):
            del self.pages[page]
        elif isinstance(page, str):
            for pg in self.pages:
                if pg.name == page:
                    self.pages.remove(pg)
                    return
        elif isinstance(page, Page):
            self.pages.remove(page)

    @property
    def modified(self) -> str:
        """
        Current timestamp in Draw.io format.

        Returns:
            ISO format timestamp string
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def agent(self) -> str:
        """
        User agent string identifying the generator.

        Returns:
            Agent string with Python and od-do version info
        """
        python_version = f"{version_info.major}.{version_info.minor}"
        return f"Python {python_version}, od-do"

    @property
    def etag(self) -> Optional[str]:
        """
        Entity tag for caching (not used by od-do).

        Returns:
            None (Draw.io includes this but we don't use it)
        """
        return None

    @property
    def xml(self) -> str:
        """
        Generate complete XML for the file.

        Combines all pages into a single Draw.io XML document.

        Adapted from drawpyo.file.File.xml

        Returns:
            Complete Draw.io XML string
        """
        xml_string = self.xml_open_tag
        for page in self.pages:
            xml_string += "\n  " + page.xml
        xml_string += "\n" + self.xml_close_tag
        return xml_string

    def write(self, **kwargs: Any) -> str:
        """
        Write the file to disk.

        Adapted from drawpyo.file.File.write

        Args:
            file_path: Override the file path (optional)
            file_name: Override the file name (optional)
            overwrite: Whether to overwrite existing files (default: True)

        Returns:
            Full path to the written file
        """
        # Allow overriding file path and name
        write_path = kwargs.get("file_path", self.file_path)
        write_name = kwargs.get("file_name", self.file_name)
        overwrite = kwargs.get("overwrite", True)

        # Create directory if it doesn't exist
        if not path.exists(write_path):
            makedirs(write_path)

        # Determine write mode
        mode = "w" if overwrite else "x"

        # Write XML to file
        full_path = path.join(write_path, write_name)
        with open(full_path, mode, encoding="utf-8") as f:
            f.write(self.xml)

        return full_path
