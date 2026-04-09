"""
Example 04: Rotation Offset

Demonstrates how rotation_offset changes the pivot point for rotation.
The key concept: offset first, then rotate around the offset pivot point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block, Circle


class Bar(diagram.Diagram):
    """A simple bar with a marker at one end."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=100,
            height=20,
            fill="#3498db",
            stroke="#2980b9",
            stroke_width=2,
        )
        Circle(
            parent=self, ul=(5, 5), radius=5, fill="#e74c3c", stroke="#c0392b", stroke_width=1
        )


class Square(diagram.Diagram):
    """A simple square for demonstrating rotation offset."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=50,
            height=30,
            fill="#e74c3c",
            stroke="#c0392b",
            stroke_width=2,
        )


class PivotMarker(diagram.Diagram):
    """A marker to show pivot points."""

    def draw(self):
        Circle(parent=self, ul=(0, 0), radius=5, fill="#f39c12", stroke="#000", stroke_width=1)


class RotationOffsetDiagram(diagram.Diagram):
    def draw(self):
        Bar(parent=self, ul=(50, 100), rotation=0)
        Bar(parent=self, ul=(50, 100), rotation=30)
        Bar(parent=self, ul=(50, 100), rotation=60)
        Bar(parent=self, ul=(50, 100), rotation=90)

        Bar(parent=self, ul=(250, 100), rotation=0, rotation_offset=(50, 10))
        Bar(parent=self, ul=(250, 100), rotation=45, rotation_offset=(50, 10))
        Bar(parent=self, ul=(250, 100), rotation=90, rotation_offset=(50, 10))
        Bar(parent=self, ul=(250, 100), rotation=135, rotation_offset=(50, 10))

        Bar(parent=self, ul=(500, 100), rotation=0, rotation_offset=(100, 10))
        Bar(parent=self, ul=(500, 100), rotation=45, rotation_offset=(100, 10))
        Bar(parent=self, ul=(500, 100), rotation=90, rotation_offset=(100, 10))
        Bar(parent=self, ul=(500, 100), rotation=135, rotation_offset=(100, 10))

        Square(parent=self, ul=(50, 300))
        Square(parent=self, ul=(50, 300), rotation=180, rotation_offset=(100, 100))
        PivotMarker(parent=self, ul=(150, 400))


if __name__ == "__main__":
    cli()
