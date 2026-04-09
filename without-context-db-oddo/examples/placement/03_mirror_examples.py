"""
Example 03: Mirror Examples

Demonstrates MX (mirror X), MY (mirror Y), and MX_MY (mirror both).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block


class LShape(diagram.Diagram):
    """An L-shaped component to clearly show orientation."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=60,
            height=20,
            fill="#9b59b6",
            stroke="#8e44ad",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(0, 0),
            width=20,
            height=60,
            fill="#9b59b6",
            stroke="#8e44ad",
            stroke_width=2,
        )
        Block(
            parent=self,
            ul=(0, 0),
            width=15,
            height=15,
            fill="#f39c12",
            stroke="#e67e22",
            stroke_width=1,
        )


class MirrorExamplesDiagram(diagram.Diagram):
    def draw(self):
        LShape(parent=self, ul=(50, 50))
        LShape(parent=self, ul=(200, 50), mirror="MY")
        LShape(parent=self, ul=(350, 50), mirror="MX")
        LShape(parent=self, ul=(500, 50), mirror="MX_MY")

        LShape(parent=self, ul=(50, 200))
        LShape(parent=self, ul=(200, 200), rotation=90)
        LShape(parent=self, ul=(350, 200), rotation=90, mirror="MY")
        LShape(parent=self, ul=(500, 200), rotation=90, mirror="MX")


if __name__ == "__main__":
    cli()
