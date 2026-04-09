import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from od_do import cli
from od_do.diagram.base import Diagram

from diagram_libs.basic_circuit_elements import AND, OR


class ANDORDemo(Diagram):
    """Demo showing AND and OR gates with various rotations."""

    render_padding = 100

    def draw(self):
        start_x = 100
        start_y = 100
        col_spacing = 200
        row_spacing = 200

        # Row 1: AND gates with rotations
        AND(parent=self, ul=(start_x, start_y), label="AND 0")
        AND(parent=self, ul=(start_x + col_spacing, start_y), rotation=90, label="AND 90")
        AND(parent=self, ul=(start_x + col_spacing * 2, start_y), rotation=180, label="AND 180")
        AND(parent=self, ul=(start_x + col_spacing * 3, start_y), rotation=270, label="AND 270")

        # Row 2: NAND gates with rotations
        AND(parent=self, ul=(start_x, start_y + row_spacing), invert=True, label="NAND 0")
        AND(
            parent=self,
            ul=(start_x + col_spacing, start_y + row_spacing),
            invert=True,
            rotation=90,
            label="NAND 90",
        )
        AND(
            parent=self,
            ul=(start_x + col_spacing * 2, start_y + row_spacing),
            invert=True,
            rotation=180,
            label="NAND 180",
        )
        AND(
            parent=self,
            ul=(start_x + col_spacing * 3, start_y + row_spacing),
            invert=True,
            rotation=270,
            label="NAND 270",
        )

        # Row 3: OR gates with rotations
        OR(parent=self, ul=(start_x, start_y + row_spacing * 2), label="OR 0")
        OR(
            parent=self,
            ul=(start_x + col_spacing, start_y + row_spacing * 2),
            rotation=90,
            label="OR 90",
        )
        OR(
            parent=self,
            ul=(start_x + col_spacing * 2, start_y + row_spacing * 2),
            rotation=180,
            label="OR 180",
        )
        OR(
            parent=self,
            ul=(start_x + col_spacing * 3, start_y + row_spacing * 2),
            rotation=270,
            label="OR 270",
        )

        # Row 4: NOR gates with rotations
        OR(parent=self, ul=(start_x, start_y + row_spacing * 3), invert=True, label="NOR 0")
        OR(
            parent=self,
            ul=(start_x + col_spacing, start_y + row_spacing * 3),
            invert=True,
            rotation=90,
            label="NOR 90",
        )
        OR(
            parent=self,
            ul=(start_x + col_spacing * 2, start_y + row_spacing * 3),
            invert=True,
            rotation=180,
            label="NOR 180",
        )
        OR(
            parent=self,
            ul=(start_x + col_spacing * 3, start_y + row_spacing * 3),
            invert=True,
            rotation=270,
            label="NOR 270",
        )


if __name__ == "__main__":
    cli()
