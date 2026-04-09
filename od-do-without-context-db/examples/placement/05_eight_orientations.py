"""
Example 05: Eight Orientations

Demonstrates all 8 possible orientations from combining
4 rotations (R0, R90, R180, R270) with 2 mirror states (none, MY).
This is commonly used in PCB design and IC placement.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block


class ICPackage(diagram.Diagram):
    """An IC package with pin 1 indicator."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=80,
            height=40,
            fill="#2c3e50",
            stroke="#1a252f",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(5, 5),
            width=10,
            height=10,
            fill="#ecf0f1",
            stroke="#bdc3c7",
            stroke_width=1,
        )


class EightOrientationsDiagram(diagram.Diagram):
    def draw(self):
        ICPackage(parent=self, ul=(50, 50), rotation=0)
        ICPackage(parent=self, ul=(200, 50), rotation=90)
        ICPackage(parent=self, ul=(350, 50), rotation=180)
        ICPackage(parent=self, ul=(500, 50), rotation=270)

        ICPackage(parent=self, ul=(50, 200), rotation=0, mirror="MY")
        ICPackage(parent=self, ul=(200, 200), rotation=90, mirror="MY")
        ICPackage(parent=self, ul=(350, 200), rotation=180, mirror="MY")
        ICPackage(parent=self, ul=(500, 200), rotation=270, mirror="MY")


if __name__ == "__main__":
    cli()
