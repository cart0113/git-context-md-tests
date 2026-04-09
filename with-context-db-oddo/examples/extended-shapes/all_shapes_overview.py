"""
Overview of all extended shapes available in OD-DO.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli, colors
from od_do.diagram import Diagram
from od_do.shapes import curves, polygon, annotations, flowchart, Block
from od_do.shapes.ellipse import Ellipse


class AllShapesOverviewDiagram(Diagram):
    def draw(self):
        y_offset = 0
        section_height = 180
        x_start = 50

        self._draw_section_label(x_start, y_offset + 20, "CURVES")
        curves.QuadraticBezier(
            parent=self,
            start=(x_start, y_offset + 100),
            control=(x_start + 50, y_offset + 40),
            end=(x_start + 100, y_offset + 100),
            stroke=colors.BLUE,
            stroke_width=2,
        )
        curves.CubicBezier(
            parent=self,
            start=(x_start + 130, y_offset + 100),
            control1=(x_start + 155, y_offset + 40),
            control2=(x_start + 205, y_offset + 40),
            end=(x_start + 230, y_offset + 100),
            stroke=colors.RED,
            stroke_width=2,
        )
        curves.Arc(
            parent=self,
            center=(x_start + 310, y_offset + 80),
            radius=35,
            start_angle=0,
            end_angle=270,
            stroke=colors.GREEN,
            stroke_width=2,
        )
        curves.SemiCircle(
            parent=self,
            center=(x_start + 400, y_offset + 80),
            radius=30,
            direction="up",
            stroke=colors.PURPLE,
            fill=colors.LIGHT_PURPLE,
            stroke_width=2,
        )

        y_offset += section_height

        self._draw_section_label(x_start, y_offset + 20, "POLYGONS")
        polygon.Triangle(
            parent=self,
            center=(x_start + 40, y_offset + 80),
            radius=35,
            fill=colors.LIGHT_RED,
            stroke=colors.DARK_RED,
            stroke_width=2,
        )
        polygon.Pentagon(
            parent=self,
            center=(x_start + 130, y_offset + 80),
            radius=35,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )
        polygon.Hexagon(
            parent=self,
            center=(x_start + 220, y_offset + 80),
            radius=35,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )
        polygon.Octagon(
            parent=self,
            center=(x_start + 310, y_offset + 80),
            radius=35,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=2,
        )
        polygon.Star(
            parent=self,
            center=(x_start + 400, y_offset + 80),
            outer_radius=40,
            inner_radius=18,
            num_points=5,
            fill=colors.GOLD,
            stroke=colors.DARK_ORANGE,
            stroke_width=2,
        )

        y_offset += section_height

        self._draw_section_label(x_start, y_offset + 20, "FLOWCHART SHAPES")
        flowchart.Diamond(
            parent=self,
            center=(x_start + 50, y_offset + 80),
            width=70,
            height=50,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=2,
        )
        flowchart.Parallelogram(
            parent=self,
            ll=(x_start + 110, y_offset + 105),
            width=70,
            height=40,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )
        flowchart.Document(
            parent=self,
            ll=(x_start + 220, y_offset + 105),
            width=70,
            height=45,
            fill=colors.WHITE,
            stroke=colors.BLACK,
            stroke_width=2,
        )
        flowchart.Cylinder(
            parent=self,
            center=(x_start + 345, y_offset + 80),
            width=50,
            height=70,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
        )
        flowchart.Cloud(
            parent=self,
            center=(x_start + 440, y_offset + 80),
            width=80,
            height=60,
            fill=colors.MD_CYAN,
            stroke=colors.TEAL,
            stroke_width=2,
        )

        y_offset += section_height

        self._draw_section_label(x_start, y_offset + 20, "ANNOTATIONS")
        Block(
            parent=self,
            ll=(x_start, y_offset + 90),
            width=100,
            height=50,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=1,
        )
        annotations.DimensionLine(
            parent=self,
            start=(x_start, y_offset + 90),
            end=(x_start + 100, y_offset + 90),
            offset=20,
            stroke=colors.BLACK,
            stroke_width=1,
        )
        annotations.Callout(
            parent=self,
            target=(x_start + 250, y_offset + 100),
            box_center=(x_start + 350, y_offset + 60),
            box_width=80,
            box_height=35,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            stroke_width=1,
        )
        annotations.LeaderLine(
            parent=self,
            start=(x_start + 450, y_offset + 100),
            elbow=(x_start + 500, y_offset + 70),
            end=(x_start + 530, y_offset + 70),
            stroke=colors.DARK_GRAY,
            stroke_width=1,
        )

        y_offset += section_height

        self._draw_section_label(x_start, y_offset + 20, "ELLIPSE")
        Ellipse(
            parent=self,
            center=(x_start + 70, y_offset + 80),
            radius_x=60,
            radius_y=35,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            stroke_width=2,
        )
        Ellipse(
            parent=self,
            center=(x_start + 200, y_offset + 80),
            radius_x=30,
            radius_y=50,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.PURPLE,
            stroke_width=2,
        )

    def _draw_section_label(self, x, y, text):
        pass


if __name__ == "__main__":
    cli()
