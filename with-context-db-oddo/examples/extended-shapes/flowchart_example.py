"""
Example demonstrating flowchart shapes: diamond, parallelogram, document,
cylinder, cloud, terminator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli
from od_do.diagram import Diagram
from od_do.shapes import flowchart
from od_do import colors


class FlowchartExampleDiagram(Diagram):
    def draw(self):
        flowchart.Diamond(
            parent=self,
            center=(100, 80),
            width=100,
            height=70,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=2,
        )

        flowchart.Parallelogram(
            parent=self,
            ll=(200, 115),
            width=100,
            height=60,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )

        flowchart.Document(
            parent=self,
            ll=(370, 115),
            width=100,
            height=60,
            fill=colors.WHITE,
            stroke=colors.BLACK,
            stroke_width=2,
        )

        flowchart.Cylinder(
            parent=self,
            center=(100, 220),
            width=80,
            height=100,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
        )

        flowchart.Cloud(
            parent=self,
            center=(250, 220),
            width=120,
            height=80,
            fill=colors.MD_CYAN,
            stroke=colors.TEAL,
            stroke_width=2,
        )

        flowchart.Terminator(
            parent=self,
            ll=(320, 260),
            width=120,
            height=50,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )

        flowchart.Diamond(
            parent=self,
            center=(500, 80),
            width=80,
            height=100,
            fill=colors.LIGHT_RED,
            stroke=colors.DARK_RED,
            stroke_width=2,
        )

        flowchart.Parallelogram(
            parent=self,
            ll=(450, 260),
            width=100,
            height=50,
            slant=30,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.DARK_PURPLE,
            stroke_width=2,
        )


if __name__ == "__main__":
    cli()
