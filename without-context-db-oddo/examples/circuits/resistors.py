import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from od_do import cli, colors
from od_do.diagram.base import Diagram
from diagram_libs.basic_circuit_elements import Resistor


class ResistorsDemo(Diagram):
    render_padding = 100

    def draw(self):
        start_x = 100
        start_y = 100
        col_spacing = 200
        row_spacing = 150

        # Row 1: Styles
        Resistor(parent=self, ul=(start_x, start_y), label="American")
        Resistor(
            parent=self, ul=(start_x + col_spacing, start_y), style="european", label="European"
        )
        Resistor(
            parent=self,
            ul=(start_x + col_spacing * 2, start_y),
            style="european",
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
            label="Filled",
        )
        Resistor(
            parent=self,
            ul=(start_x + col_spacing * 3, start_y),
            stroke=colors.DARK_RED,
            stroke_width=2,
            label="Custom stroke",
        )

        # Row 2: Rotations
        Resistor(parent=self, ul=(start_x, start_y + row_spacing), rotation=90, label="R90")
        Resistor(
            parent=self,
            ul=(start_x + col_spacing, start_y + row_spacing),
            rotation=180,
            label="R180",
        )
        Resistor(
            parent=self,
            ul=(start_x + col_spacing * 2, start_y + row_spacing),
            rotation=270,
            label="R270",
        )
        Resistor(
            parent=self,
            ul=(start_x + col_spacing * 3, start_y + row_spacing),
            style="european",
            rotation=90,
            label="EU R90",
        )

        # Row 3: Sizes
        Resistor(
            parent=self,
            ul=(start_x, start_y + row_spacing * 2),
            body_width=80,
            body_height=30,
            label="Larger",
        )
        Resistor(
            parent=self,
            ul=(start_x + col_spacing, start_y + row_spacing * 2),
            body_width=40,
            body_height=15,
            label="Smaller",
        )


if __name__ == "__main__":
    cli()
