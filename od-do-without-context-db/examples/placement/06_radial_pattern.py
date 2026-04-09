"""
Example 06: Radial Pattern

Demonstrates using rotation_offset to create radial/circular patterns
by rotating elements around a central point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import diagram, cli
from od_do.shapes import Block, Circle


class Petal(diagram.Diagram):
    """A petal-like element."""

    def draw(self):
        Block(
            parent=self,
            ul=(0, 0),
            width=30,
            height=10,
            fill="#e74c3c",
            stroke="#c0392b",
            stroke_width=1,
        )


class GearTooth(diagram.Diagram):
    """A gear tooth element."""

    def draw(self):
        Block(
            parent=self,
            ul=(-5, 0),
            width=10,
            height=20,
            fill="#95a5a6",
            stroke="#7f8c8d",
            stroke_width=1,
        )


class HourMarker(diagram.Diagram):
    """A clock hour marker."""

    def draw(self):
        Block(
            parent=self,
            ul=(-3, 0),
            width=6,
            height=15,
            fill="#2c3e50",
            stroke="#1a252f",
            stroke_width=1,
        )


class CenterCircle(diagram.Diagram):
    """Center circle for flower."""

    def draw(self):
        Circle(parent=self, ul=(0, 0), radius=20, fill="#f1c40f", stroke="#f39c12", stroke_width=2)


class GearBody(diagram.Diagram):
    """Gear body with center hole."""

    def draw(self):
        Circle(parent=self, ul=(0, 0), radius=45, fill="#7f8c8d", stroke="#6c7a7d", stroke_width=2)
        Circle(
            parent=self, ul=(20, 20), radius=15, fill="#bdc3c7", stroke="#95a5a6", stroke_width=1
        )


class ClockFace(diagram.Diagram):
    """Clock face circle."""

    def draw(self):
        Circle(parent=self, ul=(0, 0), radius=80, fill="#ecf0f1", stroke="#2c3e50", stroke_width=3)


class RadialPatternDiagram(diagram.Diagram):
    def draw(self):
        center_x, center_y = 150, 200

        for i in range(12):
            angle = i * 30
            Petal(
                parent=self,
                ul=(center_x - 15, center_y - 80),
                rotation=angle,
                rotation_offset=(15, 80),
            )

        CenterCircle(parent=self, ul=(center_x - 20, center_y - 20))

        gear_center_x, gear_center_y = 400, 200

        for i in range(16):
            angle = i * (360 / 16)
            GearTooth(
                parent=self,
                ul=(gear_center_x, gear_center_y - 60),
                rotation=angle,
                rotation_offset=(0, 60),
            )

        GearBody(parent=self, ul=(gear_center_x - 45, gear_center_y - 45))

        dial_center_x, dial_center_y = 650, 200

        for i in range(12):
            angle = i * 30
            HourMarker(
                parent=self,
                ul=(dial_center_x, dial_center_y - 70),
                rotation=angle,
                rotation_offset=(0, 70),
            )

        ClockFace(parent=self, ul=(dial_center_x - 80, dial_center_y - 80))


if __name__ == "__main__":
    cli()
