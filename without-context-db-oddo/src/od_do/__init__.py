"""
od-do: A Python object-based diagramming toolkit.

Example:
    from od_do import diagram, shapes, paths, colors

    class MyDiagram(diagram.Diagram):
        def draw(self):
            block = shapes.block(
                parent=self,
                ll=(100, 200),
                width=150,
                height=80,
                fill=colors.RED,
                stroke=colors.BLACK,
            )

            paths.line(
                parent=self,
                start=block.ll,
                points=["D20", "R30"],
                color=colors.BLUE,
            )

    diag = MyDiagram()
    diag.render("output/diagram.svg")
"""

__version__ = "0.1.0"

from .cli import cli
from . import diagram
from . import shapes
from . import paths
from . import colors
from . import markers
from .geometry import Point, BBox
from .markers import Arrow, Circle, Square, Diamond, Bar, LINE_STYLES, MARKER_SIZES, MARKER_LENGTHS
