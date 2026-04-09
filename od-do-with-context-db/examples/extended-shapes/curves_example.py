"""
Example demonstrating curve shapes: Bezier curves, arcs, and semi-circles.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli
from od_do.diagram import Diagram
from od_do.shapes import curves
from od_do import colors


class CurvesExampleDiagram(Diagram):
    def draw(self):
        curves.QuadraticBezier(
            parent=self,
            start=(50, 150),
            control=(125, 50),
            end=(200, 150),
            stroke=colors.BLUE,
            stroke_width=2,
        )

        curves.CubicBezier(
            parent=self,
            start=(250, 150),
            control1=(280, 50),
            control2=(370, 50),
            end=(400, 150),
            stroke=colors.RED,
            stroke_width=2,
        )

        curves.Arc(
            parent=self,
            center=(500, 100),
            radius=50,
            start_angle=0,
            end_angle=270,
            stroke=colors.GREEN,
            stroke_width=2,
        )

        curves.SemiCircle(
            parent=self,
            center=(100, 280),
            radius=40,
            direction="up",
            stroke=colors.PURPLE,
            fill=colors.LIGHT_PURPLE,
            stroke_width=2,
        )

        curves.SemiCircle(
            parent=self,
            center=(200, 280),
            radius=40,
            direction="down",
            stroke=colors.DARK_ORANGE,
            fill=colors.LIGHT_ORANGE,
            stroke_width=2,
        )

        curves.SemiCircle(
            parent=self,
            center=(300, 280),
            radius=40,
            direction="left",
            stroke=colors.TEAL,
            fill=colors.MD_CYAN,
            stroke_width=2,
        )

        curves.SemiCircle(
            parent=self,
            center=(400, 280),
            radius=40,
            direction="right",
            stroke=colors.PURPLE,
            fill=colors.LIGHT_PURPLE,
            stroke_width=2,
        )

        curves.Arc(
            parent=self,
            center=(550, 280),
            radius=50,
            radius_y=30,
            start_angle=30,
            end_angle=150,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
        )


if __name__ == "__main__":
    cli()
