"""
Example 07: Nested Placements

Demonstrates creating hierarchical diagrams where placements contain
other placements, enabling modular and reusable diagram components.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block, Circle


class LED(diagram.Diagram):
    """A simple LED component."""

    def draw(self):
        Circle(parent=self, ul=(0, 0), radius=8, fill="#00ff00", stroke="#009900", stroke_width=2)


class Resistor(diagram.Diagram):
    """A simple resistor component."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=30,
            height=10,
            fill="#d4a574",
            stroke="#a67c52",
            stroke_width=1,
        )


class LEDRow(diagram.Diagram):
    """A row of 4 LEDs - nested placement."""

    def draw(self):
        for i in range(4):
            LED(parent=self, ul=(i * 25, 0))


class LEDMatrix(diagram.Diagram):
    """A 4x4 LED matrix - nested placements."""

    def draw(self):
        for j in range(4):
            LEDRow(parent=self, ul=(0, j * 25))


class PCBModule(diagram.Diagram):
    """A PCB module containing LED matrix and resistors."""

    def draw(self):
        LEDMatrix(parent=self, ul=(10, 10))
        for i in range(4):
            Resistor(parent=self, ul=(120, 10 + i * 25))
        Block(
            parent=self,
            ul=(0, 0),
            width=160,
            height=110,
            fill=None,
            stroke="#27ae60",
            stroke_width=3,
        )


class NestedPlacementsDiagram(diagram.Diagram):
    def draw(self):
        LED(parent=self, ul=(50, 50))
        Resistor(parent=self, ul=(100, 50))

        LEDRow(parent=self, ul=(50, 100))

        LEDMatrix(parent=self, ul=(50, 150))

        LEDMatrix(parent=self, ul=(250, 150), rotation=45)

        LEDMatrix(parent=self, ul=(400, 150), mirror="MY")

        PCBModule(parent=self, ul=(50, 300))

        PCBModule(parent=self, ul=(300, 350), rotation=90)


if __name__ == "__main__":
    cli()
