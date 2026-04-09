"""
Draw.io backend for OD-DO.

Uses the od_do.drawio package (adapted from drawpyo) to generate
Draw.io compatible XML files.
"""

import os
from typing import List

from .base import Backend
from ...shapes.base import Shape, Rectangle, Circle
from ...drawio import File, Page, Object


class DrawIOBackend(Backend):
    """
    Backend for rendering diagrams to Draw.io format.

    Converts OD-DO shapes to Draw.io XML using the internal drawio package.
    """

    def render(self, shapes: List[Shape], output_path: str, **kwargs) -> None:
        """
        Render shapes to a Draw.io file.

        Args:
            shapes: List of shapes to render
            output_path: Path where the .drawio file should be saved
            **kwargs: Additional rendering options
        """
        # Extract directory and filename from output_path
        file_dir = os.path.dirname(output_path) or "."
        file_name = os.path.basename(output_path)

        # Create Draw.io file and page
        file = File(file_name=file_name, file_path=file_dir)
        page = Page(file=file)

        # Add shapes to page
        for shape in shapes:
            self._add_shape_to_page(page, shape)

        # Write to disk
        file.write()

    def _add_shape_to_page(self, page: Page, shape: Shape) -> None:
        """
        Convert an OD-DO shape to a Draw.io object and add to page.

        Args:
            page: Draw.io page to add object to
            shape: OD-DO shape to convert
        """
        # Determine shape type
        if isinstance(shape, Circle):
            shape_type = "ellipse"
        elif isinstance(shape, Rectangle):
            shape_type = "rectangle"
        else:
            shape_type = "rectangle"  # Default

        # Create Draw.io object
        obj = Object(
            page=page,
            value="",
            shape=shape_type,
            position=(shape.x, shape.y),
            width=shape.width,
            height=shape.height,
            fillColor=shape.fill,
            strokeColor=shape.stroke,
            strokeWidth=int(shape.stroke_width) if shape.stroke_width else None,
        )
