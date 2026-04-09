"""Charge pump voltage divider circuit diagram using OD-DO."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from od_do import cli, colors
from od_do.diagram.base import Diagram
from od_do import paths
from od_do.shapes.text import Text
from diagram_libs.basic_circuit_elements import (
    Capacitor,
    SwitchClosed,
    Battery,
)


class ChargePumpSeries(Diagram):
    """Series phase: VDD -> Cfly -> Cload -> GND"""

    def draw(self):
        sw = colors.BLACK
        sw_w = 2.5
        lbl = colors.Color.resolve_color(("#333333", 1.0))
        title_c = colors.Color.resolve_color(("#2980b9", 1.0))

        Text(parent=self, position=(300, 20), content="Series Phase (CLK low)",
             font_size=18, color=title_c, font_weight="bold", align="center")

        vdd = Battery(parent=self, ul=(50, 60), label="VDD")

        sw1 = SwitchClosed(parent=self, ul=(130, 70), label="SW1 (ON)")
        paths.line(parent=self, start_point=vdd.terminal_top,
                   points=[sw1.terminal_left], width=sw_w, color=sw)

        cfly = Capacitor(parent=self, ul=(250, 55), label="Cfly")
        paths.line(parent=self, start_point=sw1.terminal_right,
                   points=[(250, sw1.terminal_right[1]),
                           (250, cfly.terminal_top[1])],
                   width=sw_w, color=sw)
        Text(parent=self, position=(280, 48), content="top_fly",
             font_size=11, color=lbl)

        sw2 = SwitchClosed(parent=self, ul=(330, 70), label="SW2 (ON)")
        paths.line(parent=self, start_point=cfly.terminal_bottom,
                   points=[(cfly.terminal_bottom[0], sw2.terminal_left[1]),
                           sw2.terminal_left],
                   width=sw_w, color=sw)
        Text(parent=self, position=(310, 128), content="bot_fly",
             font_size=11, color=lbl)

        cload = Capacitor(parent=self, ul=(470, 55), label="Cload (18fF)")
        paths.line(parent=self, start_point=sw2.terminal_right,
                   points=[(470, sw2.terminal_right[1]),
                           (470, cload.terminal_top[1])],
                   width=sw_w, color=sw)

        gnd_y = 180
        paths.line(parent=self, start_point=cload.terminal_bottom,
                   points=[(cload.terminal_bottom[0], gnd_y)],
                   width=sw_w, color=sw)
        paths.line(parent=self, start_point=vdd.terminal_bottom,
                   points=[(vdd.terminal_bottom[0], gnd_y),
                           (cload.terminal_bottom[0], gnd_y)],
                   width=sw_w, color=sw)
        Text(parent=self, position=(300, gnd_y + 15), content="GND",
             font_size=12, color=lbl, align="center")

        off_c = colors.Color.resolve_color(("#aaaaaa", 1.0))
        Text(parent=self, position=(380, 168), content="SW3,SW4 OFF",
             font_size=10, color=off_c)


class ChargePumpParallel(Diagram):
    """Parallel phase: Cfly in parallel with Cload"""

    def draw(self):
        sw = colors.BLACK
        sw_w = 2.5
        lbl = colors.Color.resolve_color(("#333333", 1.0))
        title_c = colors.Color.resolve_color(("#c0392b", 1.0))

        Text(parent=self, position=(260, 20), content="Parallel Phase (CLK high)",
             font_size=18, color=title_c, font_weight="bold", align="center")

        cfly = Capacitor(parent=self, ul=(120, 55), label="Cfly")
        Text(parent=self, position=(150, 48), content="top_fly",
             font_size=11, color=lbl)

        sw3 = SwitchClosed(parent=self, ul=(220, 60), label="SW3 (ON)")
        paths.line(parent=self, start_point=cfly.terminal_top,
                   points=[(cfly.terminal_top[0], sw3.terminal_left[1]),
                           sw3.terminal_left],
                   width=sw_w, color=sw)

        cload = Capacitor(parent=self, ul=(380, 55), label="Cload (18fF)")
        paths.line(parent=self, start_point=sw3.terminal_right,
                   points=[(380, sw3.terminal_right[1]),
                           (380, cload.terminal_top[1])],
                   width=sw_w, color=sw)

        sw4 = SwitchClosed(parent=self, ul=(120, 140), label="SW4 (ON)")
        paths.line(parent=self, start_point=cfly.terminal_bottom,
                   points=[(cfly.terminal_bottom[0], sw4.terminal_left[1]),
                           sw4.terminal_left],
                   width=sw_w, color=sw)
        Text(parent=self, position=(150, 128), content="bot_fly",
             font_size=11, color=lbl)

        gnd_y = 190
        paths.line(parent=self, start_point=sw4.terminal_right,
                   points=[(sw4.terminal_right[0] + 20, gnd_y)],
                   width=sw_w, color=sw)
        paths.line(parent=self, start_point=cload.terminal_bottom,
                   points=[(cload.terminal_bottom[0], gnd_y),
                           (sw4.terminal_right[0] + 20, gnd_y)],
                   width=sw_w, color=sw)
        Text(parent=self, position=(280, gnd_y + 15), content="GND",
             font_size=12, color=lbl, align="center")

        off_c = colors.Color.resolve_color(("#aaaaaa", 1.0))
        Text(parent=self, position=(50, 80), content="SW1,SW2 OFF",
             font_size=10, color=off_c)
        Text(parent=self, position=(50, 95), content="VDD disconnected",
             font_size=10, color=off_c)


if __name__ == "__main__":
    cli()
