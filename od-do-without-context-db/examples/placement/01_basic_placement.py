"""
Example 01: Basic Placement

Demonstrates placing a sub-diagram at different positions
using the parent= constructor pattern with ul (upper-left) positioning.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block, Circle


class Component(diagram.Diagram):
    """A simple component with a rectangle and circle."""

    def draw(self):
        Block(
            parent=self,
            ll=(0, 40),
            width=60,
            height=40,
            fill="#3498db",
            stroke="#2980b9",
            stroke_width=2,
        )
        Circle(
            parent=self,
            center=(60, 20),
            radius=10,
            fill="#e74c3c",
            stroke="#c0392b",
            stroke_width=2,
        )


class BasicPlacementDiagram(diagram.Diagram):
    def draw(self):
        Component(parent=self, ul=(50, 50))
        Component(parent=self, ul=(200, 50))
        Component(parent=self, ul=(350, 50))

        Component(parent=self, ul=(50, 150))
        Component(parent=self, ul=(200, 150))
        Component(parent=self, ul=(350, 150))

        Component(parent=self, ul=(50, 250))
        Component(parent=self, ul=(200, 250))
        Component(parent=self, ul=(350, 250))


if __name__ == "__main__":
    cli()
