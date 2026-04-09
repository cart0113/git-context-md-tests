import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from od_do import cli, colors
from od_do.diagram.base import Diagram
from od_do.paths import Line
from diagram_libs.basic_circuit_elements import (
    Resistor,
    Capacitor,
    Battery,
    AND,
    OR,
    XOR,
    Buffer,
    DFlipFlop,
    WireJump,
    SwitchOpen,
    SwitchClosed,
    Junction,
)


class SampleCircuit(Diagram):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self):
        from od_do.colors import Color
        stroke = Color.resolve_color(("#707070", 0.9))
        stroke_width = 3.0

        # Row 1: Basic passive components
        Battery(parent=self, ul=(50, 50), label="Battery")
        Capacitor(parent=self, ul=(130, 50), label="Capacitor")
        Resistor(parent=self, ul=(220, 75), label="Resistor")

        # Row 2: Basic logic gates
        AND(parent=self, ul=(50, 160), label="AND")
        OR(parent=self, ul=(140, 160), label="OR")
        XOR(parent=self, ul=(230, 160), label="XOR")
        Buffer(parent=self, ul=(340, 165), label="Buffer")

        # Row 3: Inverted gates
        AND(parent=self, ul=(50, 280), invert=True, label="NAND")
        OR(parent=self, ul=(140, 280), invert=True, label="NOR")
        XOR(parent=self, ul=(230, 280), invert=True, label="XNOR")
        Buffer(parent=self, ul=(340, 285), invert=True, label="NOT")

        # Row 4: D Flip-Flop
        DFlipFlop(parent=self, ul=(50, 400), label="D Flip-Flop")

        # Row 4: Wire components and switches
        SwitchOpen(parent=self, ul=(160, 420), label="Open")
        SwitchClosed(parent=self, ul=(280, 420), label="Closed")
        WireJump(parent=self, ul=(400, 450))
        Junction(parent=self, ul=(470, 450))


if __name__ == "__main__":
    cli()
