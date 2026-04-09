"""
Example 02: Basic Rotation

Demonstrates rotation at 0, 90, 180, and 270 degrees.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block


class Arrow(diagram.Diagram):
    """An arrow-like component pointing right."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 15),
            width=50,
            height=20,
            fill="#2ecc71",
            stroke="#27ae60",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(45, 5),
            width=20,
            height=40,
            fill="#2ecc71",
            stroke="#27ae60",
            stroke_width=2,
        )


class RotationBasicDiagram(diagram.Diagram):
    def draw(self):
        Arrow(parent=self, ul=(50, 50))
        Arrow(parent=self, ul=(200, 50), rotation=90)
        Arrow(parent=self, ul=(350, 50), rotation=180)
        Arrow(parent=self, ul=(500, 50), rotation=270)

        Arrow(parent=self, ul=(50, 200), rotation=0)
        Arrow(parent=self, ul=(150, 200), rotation=45)
        Arrow(parent=self, ul=(250, 200), rotation=90)
        Arrow(parent=self, ul=(350, 200), rotation=135)
        Arrow(parent=self, ul=(450, 200), rotation=180)

        Arrow(parent=self, ul=(50, 350), rotation=180)
        Arrow(parent=self, ul=(150, 350), rotation=225)
        Arrow(parent=self, ul=(250, 350), rotation=270)
        Arrow(parent=self, ul=(350, 350), rotation=315)
        Arrow(parent=self, ul=(450, 350), rotation=360)


if __name__ == "__main__":
    cli()
