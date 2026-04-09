"""
Example demonstrating text shapes: Text, TextBox, and Label with various alignments.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from od_do import cli, colors
from od_do.diagram import Diagram
from od_do.shapes import text, Block


class TextExampleDiagram(Diagram):
    def draw(self):
        # Section 1: Basic Text with different alignments
        # Horizontal alignment demo
        text.Text(
            parent=self,
            position=(100, 50),
            content="Left aligned (default)",
            font_size=14,
            color=colors.BLACK,
            align="left",
        )

        text.Text(
            parent=self,
            position=(300, 50),
            content="Center aligned",
            font_size=14,
            color=colors.DARK_BLUE,
            align="center",
        )

        text.Text(
            parent=self,
            position=(500, 50),
            content="Right aligned",
            font_size=14,
            color=colors.DARK_GREEN,
            align="right",
        )

        # Section 2: Multiline text
        text.Text(
            parent=self,
            position=(100, 120),
            content="Multiline text\nwith automatic\nline handling",
            font_size=12,
            color=colors.BLACK,
            align="left",
        )

        text.Text(
            parent=self,
            position=(300, 120),
            content="Centered\nmultiline\ntext block",
            font_size=12,
            color=colors.PURPLE,
            align="center",
        )

        # Section 3: Font styling
        text.Text(
            parent=self,
            position=(500, 120),
            content="Bold text",
            font_size=16,
            font_weight="bold",
            color=colors.RED,
            align="right",
        )

        text.Text(
            parent=self,
            position=(500, 145),
            content="Monospace font",
            font_size=12,
            font_family="monospace",
            color=colors.DARK_GRAY,
            align="right",
        )

        # Section 4: TextBox examples
        text.TextBox(
            parent=self,
            ll=(50, 280),
            width=120,
            height=50,
            content="TextBox\nwith fill",
            font_size=12,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            stroke_width=2,
            align="center",
            valign="middle",
        )

        text.TextBox(
            parent=self,
            ll=(200, 280),
            width=120,
            height=50,
            content="Left/Top\naligned",
            font_size=11,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            align="left",
            valign="top",
        )

        text.TextBox(
            parent=self,
            ll=(350, 280),
            width=120,
            height=50,
            content="Right/Bottom\naligned",
            font_size=11,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            align="right",
            valign="bottom",
        )

        # TextBox with rounded corners
        text.TextBox(
            parent=self,
            ll=(500, 280),
            width=120,
            height=50,
            content="Rounded\ncorners",
            font_size=12,
            fill=colors.LIGHT_PURPLE,
            stroke=colors.PURPLE,
            stroke_width=2,
            corners="round",
            align="center",
            valign="middle",
        )

        # Section 5: Label examples
        text.Label(
            parent=self,
            position=(100, 340),
            content="Simple Label",
            font_size=12,
            fill=colors.WHITE,
            stroke=colors.BLACK,
            padding=6,
        )

        text.Label(
            parent=self,
            position=(250, 340),
            content="Colored Label",
            font_size=12,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            text_color=colors.DARK_GRAY,
            padding=8,
        )

        text.Label(
            parent=self,
            position=(400, 340),
            content="Rounded Label",
            font_size=12,
            fill=colors.LIGHT_BLUE,
            stroke=colors.DARK_BLUE,
            corners="very-round",
            padding=10,
        )

        text.Label(
            parent=self,
            position=(550, 340),
            content="Multi-line\nLabel",
            font_size=11,
            fill=colors.LIGHT_GREEN,
            stroke=colors.DARK_GREEN,
            padding=6,
        )

        Block(
            parent=self,
            ll=(50, 450),
            width=200,
            height=60,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
            corners="slightly-round",
        )

        # Add text on top of block (manual positioning)
        text.Text(
            parent=self,
            position=(150, 405),
            content="Block as TextBox\nbackground",
            font_size=14,
            color=colors.BLACK,
            align="center",
            valign="middle",
        )

        # Compare with native TextBox
        text.TextBox(
            parent=self,
            ll=(300, 450),
            width=200,
            height=60,
            content="Native TextBox\n(integrated)",
            font_size=14,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
            stroke_width=2,
            corners="slightly-round",
            align="center",
            valign="middle",
        )


if __name__ == "__main__":
    cli()
