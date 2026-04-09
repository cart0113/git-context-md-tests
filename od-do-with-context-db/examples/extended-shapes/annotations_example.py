"""
Example demonstrating annotation shapes: dimension lines, leader lines, callouts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli, colors
from od_do.diagram import Diagram
from od_do.shapes import annotations, Block, Circle


class AnnotationsExampleDiagram(Diagram):
    def draw(self):
        Block(
            parent=self,
            ll=(100, 200),
            width=150,
            height=80,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )

        annotations.DimensionLine(
            parent=self,
            start=(100, 200),
            end=(250, 200),
            offset=25,
            stroke=colors.BLACK,
            stroke_width=1,
        )

        annotations.DimensionLine(
            parent=self,
            start=(100, 200),
            end=(100, 120),
            offset=-25,
            stroke=colors.BLACK,
            stroke_width=1,
        )

        Circle(
            parent=self,
            center=(400, 160),
            radius=40,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )

        annotations.LeaderLine(
            parent=self,
            start=(400, 120),
            elbow=(500, 80),
            end=(550, 80),
            stroke=colors.DARK_GRAY,
            stroke_width=1,
            arrow_size=8,
        )

        annotations.Callout(
            parent=self,
            target=(175, 160),
            box_center=(350, 50),
            box_width=100,
            box_height=40,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=1,
        )

        annotations.Callout(
            parent=self,
            target=(550, 200),
            box_center=(600, 120),
            box_width=80,
            box_height=50,
            fill=colors.WHITE,
            stroke=colors.BLACK,
            stroke_width=1,
        )

        annotations.LeaderLine(
            parent=self,
            start=(250, 250),
            end=(350, 250),
            stroke=colors.RED,
            stroke_width=2,
            arrow_size=10,
        )


if __name__ == "__main__":
    cli()
