"""
Simple example diagram using OD-DO.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from od_do import cli, diagram
from od_do.shapes import Block, Circle, Rectangle


class MyDiagram(diagram.Diagram):
    def draw(self):
        Block(
            parent=self,
            ll=(100, 200),
            width=200,
            height=100,
            fill="#ff6b6b",
            stroke="#000000",
            stroke_width=2,
        )

        Circle(
            parent=self,
            center=(450, 150),
            radius=50,
            fill="#4ecdc4",
            stroke="#000000",
            stroke_width=2,
        )

        Rectangle(
            parent=self,
            ll=(500, 380),
            width=150,
            height=80,
            fill="#ffe66d",
            stroke="#000000",
            stroke_width=2,
        )


if __name__ == "__main__":
    cli()
