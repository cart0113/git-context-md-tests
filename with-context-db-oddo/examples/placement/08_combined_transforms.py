"""
Example 08: Combined Transforms

Demonstrates combining rotation, mirroring, and rotation_offset
all together for complex transformations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block


class FShape(diagram.Diagram):
    """An F-shaped component - very asymmetric to show all transforms clearly."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=15,
            height=60,
            fill="#3498db",
            stroke="#2980b9",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(0, 0),
            width=40,
            height=15,
            fill="#3498db",
            stroke="#2980b9",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(0, 25),
            width=30,
            height=10,
            fill="#3498db",
            stroke="#2980b9",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(0, 0),
            width=5,
            height=5,
            fill="#e74c3c",
            stroke="#c0392b",
            stroke_width=1,
        )


class Square(diagram.Diagram):
    """A square with corner marker."""

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
        Block(
            parent=self,
            ul=(0, 0),
            width=10,
            height=10,
            fill="#f39c12",
            stroke="#e67e22",
            stroke_width=1,
        )


class PivotMarker(diagram.Diagram):
    """A marker for pivot points."""

    def draw(self):
        Block(
            parent=self,
            ul=(-3, -3),
            width=6,
            height=6,
            fill="#2ecc71",
            stroke="#27ae60",
            stroke_width=2,
        )


class CombinedTransformsDiagram(diagram.Diagram):
    def draw(self):
        FShape(parent=self, ul=(50, 50))
        FShape(parent=self, ul=(150, 50), rotation=90)
        FShape(parent=self, ul=(250, 50), mirror="MY")
        FShape(parent=self, ul=(350, 50), rotation=90, mirror="MY")
        FShape(parent=self, ul=(450, 50), mirror="MX")
        FShape(parent=self, ul=(550, 50), rotation=90, mirror="MX")

        center_offset = (20, 30)

        FShape(parent=self, ul=(50, 200))
        FShape(parent=self, ul=(150, 200), rotation=90, rotation_offset=center_offset)
        FShape(parent=self, ul=(250, 200), rotation=180, rotation_offset=center_offset)
        FShape(parent=self, ul=(350, 200), rotation=270, rotation_offset=center_offset)

        FShape(parent=self, ul=(50, 350), rotation=45, mirror="MY", rotation_offset=center_offset)
        FShape(parent=self, ul=(150, 350), rotation=45, mirror="MX", rotation_offset=center_offset)
        FShape(parent=self, ul=(250, 350), rotation=135, mirror="MY", rotation_offset=center_offset)
        FShape(parent=self, ul=(350, 350), rotation=135, mirror="MX", rotation_offset=center_offset)

        Square(parent=self, ul=(50, 450))

        Square(parent=self, ul=(50, 450), rotation=180, rotation_offset=(100, 100))

        PivotMarker(parent=self, ul=(50 + 100, 450 + 100))


if __name__ == "__main__":
    cli()
