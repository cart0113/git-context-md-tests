"""
Example demonstrating ellipse shapes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli
from od_do.diagram import Diagram
from od_do.shapes.ellipse import Ellipse
from od_do import colors


class EllipseExampleDiagram(Diagram):
    def draw(self):
        Ellipse(
            parent=self,
            center=(100, 100),
            radius_x=80,
            radius_y=40,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )

        Ellipse(
            parent=self,
            center=(280, 100),
            radius_x=40,
            radius_y=80,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )

        Ellipse(
            parent=self,
            center=(420, 100),
            radius_x=60,
            radius_y=60,
            fill=colors.LIGHT_RED,
            stroke=colors.DARK_RED,
            stroke_width=2,
        )

        Ellipse(
            parent=self,
            center=(180, 250),
            radius_x=120,
            radius_y=50,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.DARK_PURPLE,
            stroke_width=3,
        )

        Ellipse(
            parent=self,
            center=(400, 250),
            radius_x=50,
            radius_y=30,
            fill=colors.LIGHT_ORANGE.alpha(0.6),
            stroke=colors.DARK_ORANGE,
            stroke_width=2,
        )


if __name__ == "__main__":
    cli()
