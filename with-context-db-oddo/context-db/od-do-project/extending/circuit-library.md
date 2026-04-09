---
description:
  Circuit elements library at diagram_libs/basic_circuit_elements/ — component
  list, design pattern, pin access, and how to add new elements
---

# Circuit Elements Library

Located at `diagram_libs/basic_circuit_elements/`. All components are `Diagram`
subclasses that compose od-do primitives in their `draw()` method.

## Available components

**Passive** (`circuit_elements.py`): Resistor (american/european), Capacitor,
Battery, Inductor.

**Active** (`transistors.py`): NMOS, PMOS (enhancement-mode transistors).

**Logic gates** (`logic_gates.py`): AND, OR, XOR, Buffer (all support
`invert=True` for NAND/NOR/XNOR/NOT). DFlipFlop (with optional Q-bar and
labels).

**Wiring** (`wires.py`): WireJump, SwitchOpen, SwitchClosed, Junction.

**Power/Ground** (`transistors.py`): VDD, Ground.

## Design pattern

All circuit elements follow this pattern:

1. Store custom params **before** `super().__init__(**kwargs)` (because super
   calls `draw()`).
2. Use `**kwargs` passthrough for Diagram placement options (`ul`, `rotation`,
   etc.).
3. Draw at origin `(0, 0)` — let the Diagram system handle positioning.
4. Expose pin positions as `Point` properties for wire connections.

```python
class MyComponent(Diagram):
    def __init__(self, my_param, stroke=("#707070", 0.9), **kwargs):
        self._my_param = my_param
        self._stroke = Color.resolve_color(stroke)
        super().__init__(**kwargs)  # calls draw()

    def draw(self):
        Line(parent=self, start_point=(0, 0), points=["R40"], ...)

    @property
    def terminal_left(self):
        return Point(0, self._body_height / 2)
```

## Pin access

Components expose pin positions as `Point` properties:

- Resistor: `terminal_left`, `terminal_right`.
- Capacitor/Battery: `terminal_top`, `terminal_bottom`.
- NMOS/PMOS: `gate_pin`, `drain_pin`, `source_pin`.
- Logic gates: `input_pin(index)`, `output_pin`.
- DFlipFlop: `d_pin`, `clk_pin`, `q_pin`, `qn_pin`.
- Ground: `terminal_top`. VDD: `terminal_bottom`.
