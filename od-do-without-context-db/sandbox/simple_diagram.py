"""
Simple example diagram using OD-DO.

Demonstrates:
- Shape positioning with ll, ul, lr, ur anchor points
- Accessing shape anchor points via block.points (block.points.ll, block.points.center)
- Paths with direction strings (D20, R30, U10)
- Color manipulation (alpha, lighten, darken)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from od_do import cli, colors, diagram, markers, paths, shapes


class MyDiagram(diagram.Diagram):
    units = "um"
    unit_to_pixels = 2

    def draw(self):
        # Create a block positioned by its lower-left corner
        block_0 = shapes.block(
            parent=self,
            ll=(500, 500),
            width=200,
            height=100,
            fill=("#ff6b6b", 0.5),
            stroke=("#af1b1b", 0.5),
            stroke_width=2,
            corners="round:0.05",
        )

        # Line using absolute coordinates starting from block's lower-left
        path_0 = paths.Line(
            parent=self,
            start_point=block_0.points.lr,
            points=["R100", "D100", "R100", "D10"],
            width=1,
            color=colors.GRAY.alpha(0.85),
            start_marker=markers.Square(size="medium"),
            end_marker=markers.Arrow(size="medium", invert=True),
        )

        # Line using direction strings from block's lower-left
        path_1 = paths.StrokeLine(
            parent=self,
            start_point=block_0.points.ll + (75, 50),
            points=["D30", "R20", "D30"],
            width=4,
            color=colors.RED.alpha(0.25),
            stroke_color=colors.BLUE.alpha(0.25),
            stroke_width=1,
        )

        # Rectangle positioned by its upper-right corner, aligned to block's lower-left
        shapes.rectangle(
            parent=self,
            ur=block_0.points.ll,
            width=150,
            height=80,
            fill="#ffe66d",
            stroke="#00F000",
            stroke_width=2,
        )

        # Circle positioned by center, using a color constant
        shapes.circle(
            parent=self,
            center=block_0.points.center,
            radius=30,
            fill=colors.LIGHT_BLUE.alpha(0.7),
            stroke=colors.DARK_BLUE,
            stroke_width=2,
        )

        # Line from midpoint of left edge downward
        paths.Line(
            parent=self,
            start_point=block_0.points.left(0.5),
            points=["L50", "D30", "R100"],
            width=3,
            color=colors.EMERALD,
        )


if __name__ == "__main__":
    # Ensure output directory exists
    cli()
