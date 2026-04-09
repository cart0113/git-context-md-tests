"""
Example demonstrating polygon shapes: triangles, pentagons, hexagons, stars.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli
from od_do.diagram import Diagram
from od_do.shapes import polygon
from od_do import colors


class PolygonsExampleDiagram(Diagram):
    def draw(self):
        polygon.Triangle(
            parent=self,
            center=(80, 80),
            radius=50,
            fill=colors.LIGHT_RED,
            stroke=colors.DARK_RED,
            stroke_width=2,
        )

        polygon.Pentagon(
            parent=self,
            center=(200, 80),
            radius=50,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )

        polygon.Hexagon(
            parent=self,
            center=(320, 80),
            radius=50,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )

        polygon.Octagon(
            parent=self,
            center=(440, 80),
            radius=50,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=2,
        )

        polygon.RegularPolygon(
            parent=self,
            center=(560, 80),
            radius=50,
            sides=12,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.DARK_PURPLE,
            stroke_width=2,
        )

        polygon.Star(
            parent=self,
            center=(80, 220),
            outer_radius=50,
            inner_radius=20,
            num_points=5,
            fill=colors.GOLD,
            stroke=colors.DARK_ORANGE,
            stroke_width=2,
        )

        polygon.Star(
            parent=self,
            center=(200, 220),
            outer_radius=50,
            inner_radius=30,
            num_points=6,
            fill=colors.MD_CYAN,
            stroke=colors.TEAL,
            stroke_width=2,
        )

        polygon.Star(
            parent=self,
            center=(320, 220),
            outer_radius=50,
            inner_radius=25,
            num_points=8,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.PURPLE,
            stroke_width=2,
        )

        polygon.Triangle(
            parent=self,
            center=(440, 220),
            radius=50,
            rotation=60,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
        )

        polygon.Hexagon(
            parent=self,
            center=(560, 220),
            radius=50,
            rotation=0,
            fill=colors.LIGHT_ORANGE,
            stroke=colors.DARK_ORANGE,
            stroke_width=2,
        )


if __name__ == "__main__":
    cli()
