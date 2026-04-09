# Circuit Elements

OD-DO provides a library of circuit schematic symbols for creating electronic
diagrams. Components are Diagram subclasses that support rotation, placement,
and styling.

## Importing Circuit Elements

```python
from diagram_libs.basic_circuit_elements import (
    # Passive components
    Resistor, Capacitor, Battery, Inductor,
    # Active components (transistors)
    NMOS, PMOS,
    # Logic gates
    AND, OR, XOR, Buffer, DFlipFlop,
    # Wiring elements
    WireJump, SwitchOpen, SwitchClosed, Junction,
    # Power and ground symbols
    Ground, VDD,
)
```

## Placement and Rotation

All circuit elements use the standard Diagram placement parameters:

```python
# Basic placement
AND(parent=self, ul=(100, 100))

# With rotation (degrees)
AND(parent=self, ul=(100, 100), rotation=90)
AND(parent=self, ul=(100, 100), rotation=180)
AND(parent=self, ul=(100, 100), rotation=270)

# With label
AND(parent=self, ul=(100, 100), label="U1")
```

---

## Logic Gates

### AND Gate

Rectangle with semicircle output. Set `invert=True` for NAND.

```python
# 2-input AND
AND(parent=self, ul=(100, 100))

# 3-input AND
AND(parent=self, ul=(100, 100), num_inputs=3)

# NAND gate (inverted)
AND(parent=self, ul=(100, 100), invert=True)

# With label
AND(parent=self, ul=(100, 100), label="U1")
```

| Parameter         | Type      | Default            | Description                  |
| ----------------- | --------- | ------------------ | ---------------------------- |
| `num_inputs`      | int       | 2                  | Number of input pins         |
| `invert`          | bool      | False              | Add inversion bubble (NAND)  |
| `fill`            | ColorLike | `"#eeeeee"`        | Body fill color              |
| `stroke`          | ColorLike | `("#707070", 0.9)` | Stroke color                 |
| `stroke_width`    | float     | 3.0                | Stroke width                 |
| `label`           | str       | None               | Label text below gate        |
| `body_width`      | float     | 50                 | Gate body width              |
| `body_height`     | float     | 60                 | Gate body height             |
| `terminal_length` | float     | 10                 | Length of input/output leads |

Pin access:

```python
gate = AND(parent=self, ul=(100, 100), num_inputs=2)
gate.input_pin(0)   # First input
gate.input_pin(1)   # Second input
gate.output_pin     # Output
```

### OR Gate

Curved D-shaped body with pointed output. Set `invert=True` for NOR.

```python
# 2-input OR
OR(parent=self, ul=(100, 100))

# NOR gate
OR(parent=self, ul=(100, 100), invert=True)
```

Same parameters as AND gate.

### XOR Gate

Like OR but with extra curved line at input. Set `invert=True` for XNOR.

```python
# 2-input XOR
XOR(parent=self, ul=(100, 100))

# XNOR gate
XOR(parent=self, ul=(100, 100), invert=True)
```

### Buffer / NOT Gate

Triangle shape. Set `invert=True` for NOT (inverter).

```python
# Buffer
Buffer(parent=self, ul=(100, 100))

# NOT gate (inverter)
Buffer(parent=self, ul=(100, 100), invert=True)
```

| Parameter     | Type  | Default | Description                |
| ------------- | ----- | ------- | -------------------------- |
| `invert`      | bool  | False   | Add inversion bubble (NOT) |
| `body_width`  | float | 40      | Triangle width             |
| `body_height` | float | 50      | Triangle height            |

Pin access:

```python
buf = Buffer(parent=self, ul=(100, 100))
buf.input_pin    # Input
buf.output_pin   # Output
```

---

## Sequential Logic

### D Flip-Flop

Rectangle with clock triangle indicator.

```python
# Basic D flip-flop
DFlipFlop(parent=self, ul=(100, 100))

# Show Q-bar output
DFlipFlop(parent=self, ul=(100, 100), show_qbar=True)

# Show pin labels
DFlipFlop(parent=self, ul=(100, 100), show_labels=True)
```

| Parameter     | Type  | Default | Description           |
| ------------- | ----- | ------- | --------------------- |
| `show_qbar`   | bool  | False   | Show Q-bar output     |
| `show_labels` | bool  | False   | Show D, CLK, Q labels |
| `body_width`  | float | 60      | Body width            |
| `body_height` | float | 80      | Body height           |

Pin access:

```python
ff = DFlipFlop(parent=self, ul=(100, 100))
ff.d_pin    # D input
ff.clk_pin  # Clock input
ff.q_pin    # Q output
ff.qn_pin   # Q-bar output (if show_qbar=True)
```

---

## Passive Components

### Resistor

American (zigzag) or European (rectangle) style.

```python
# American style (default)
Resistor(parent=self, ul=(100, 100))

# European style
Resistor(parent=self, ul=(100, 100), style="european")

# With label
Resistor(parent=self, ul=(100, 100), label="R1")
```

| Parameter         | Type  | Default      | Description                                       |
| ----------------- | ----- | ------------ | ------------------------------------------------- |
| `style`           | str   | `"american"` | `"american"` (zigzag) or `"european"` (rectangle) |
| `body_width`      | float | 60           | Total width including leads                       |
| `body_height`     | float | 20           | Height of zigzag/rectangle                        |
| `terminal_length` | float | 8            | Lead length beyond body                           |

Pin access:

```python
r = Resistor(parent=self, ul=(100, 100))
r.terminal_left   # Left terminal
r.terminal_right  # Right terminal
```

### Capacitor

Two parallel plates. Drawn vertically by default (terminals top/bottom).

```python
Capacitor(parent=self, ul=(100, 100))

# With label
Capacitor(parent=self, ul=(100, 100), label="C1")
```

| Parameter         | Type  | Default | Description        |
| ----------------- | ----- | ------- | ------------------ |
| `plate_width`     | float | 30      | Width of plates    |
| `gap`             | float | 9       | Gap between plates |
| `terminal_length` | float | 15      | Lead length        |

Pin access:

```python
c = Capacitor(parent=self, ul=(100, 100))
c.terminal_top     # Top terminal
c.terminal_bottom  # Bottom terminal
```

### Battery

Long plate (negative) on top, short plate (positive) on bottom. Drawn
vertically.

```python
Battery(parent=self, ul=(100, 100))

# With label
Battery(parent=self, ul=(100, 100), label="V1")
```

| Parameter           | Type  | Default | Description             |
| ------------------- | ----- | ------- | ----------------------- |
| `long_plate_width`  | float | 30      | Width of negative plate |
| `short_plate_width` | float | 16      | Width of positive plate |
| `gap`               | float | 12      | Gap between plates      |
| `terminal_length`   | float | 15      | Lead length             |

Pin access:

```python
b = Battery(parent=self, ul=(100, 100))
b.terminal_top     # Negative terminal
b.terminal_bottom  # Positive terminal
```

### Inductor

Horizontal coil with semicircular bumps.

```python
Inductor(parent=self, ul=(100, 100))

# With label
Inductor(parent=self, ul=(100, 100), label="L1")

# Custom bump count
Inductor(parent=self, ul=(100, 100), num_bumps=6)
```

| Parameter         | Type  | Default | Description                |
| ----------------- | ----- | ------- | -------------------------- |
| `body_width`      | float | 60      | Total width                |
| `body_height`     | float | 20      | Height                     |
| `terminal_length` | float | 8       | Lead length beyond body    |
| `num_bumps`       | int   | 4       | Number of semicircle coils |

Pin access:

```python
l = Inductor(parent=self, ul=(100, 100))
l.terminal_left   # Left terminal
l.terminal_right  # Right terminal
```

---

## Transistors

### NMOS

Enhancement-mode NMOS transistor. Vertical channel with gate on left, drain on
top, source on bottom. Arrow on source points INTO the channel.

```python
NMOS(parent=self, ul=(100, 100))

# With label
NMOS(parent=self, ul=(100, 100), label="M1")

# Rotated
NMOS(parent=self, ul=(100, 100), rotation=90)
```

| Parameter         | Type  | Default | Description   |
| ----------------- | ----- | ------- | ------------- |
| `body_width`      | float | 40      | Symbol width  |
| `body_height`     | float | 60      | Symbol height |
| `terminal_length` | float | 15      | Lead length   |

Pin access:

```python
n = NMOS(parent=self, ul=(100, 100))
n.gate_pin     # Gate (left)
n.drain_pin    # Drain (top)
n.source_pin   # Source (bottom)
```

### PMOS

Enhancement-mode PMOS transistor. Same as NMOS but arrow on source points AWAY
from channel, and a bubble on the gate indicates P-type.

```python
PMOS(parent=self, ul=(100, 100))

# With label
PMOS(parent=self, ul=(100, 100), label="M2")
```

Same parameters and pin access as NMOS:

```python
p = PMOS(parent=self, ul=(100, 100))
p.gate_pin     # Gate (left, with bubble)
p.drain_pin    # Drain (top)
p.source_pin   # Source (bottom)
```

---

## Power and Ground

### Ground

Standard earth ground symbol with three decreasing-width horizontal lines.

```python
Ground(parent=self, ul=(100, 100))
```

| Parameter    | Type  | Default | Description  |
| ------------ | ----- | ------- | ------------ |
| `body_width` | float | 30      | Symbol width |

Pin access:

```python
gnd = Ground(parent=self, ul=(100, 100))
gnd.terminal_top  # Connection point
```

### VDD

Power supply symbol with horizontal bar and vertical line down.

```python
VDD(parent=self, ul=(100, 100))

# Custom label
VDD(parent=self, ul=(100, 100), label="VCC")
```

| Parameter    | Type  | Default | Description  |
| ------------ | ----- | ------- | ------------ |
| `body_width` | float | 30      | Symbol width |
| `label`      | str   | "VDD"   | Label text   |

Pin access:

```python
vdd = VDD(parent=self, ul=(100, 100))
vdd.terminal_bottom  # Connection point
```

---

## Wiring Elements

### WireJump

Semicircle indicating wire crossing over another wire.

```python
WireJump(parent=self, ul=(100, 100))
```

| Parameter         | Type  | Default | Description              |
| ----------------- | ----- | ------- | ------------------------ |
| `radius`          | float | 12      | Semicircle radius        |
| `terminal_length` | float | 10      | Lead length on each side |

Pin access:

```python
jump = WireJump(parent=self, ul=(100, 100))
jump.terminal_left   # Left connection
jump.terminal_right  # Right connection
```

### Switch (Open/Closed)

```python
# Open switch
SwitchOpen(parent=self, ul=(100, 100))

# Closed switch
SwitchClosed(parent=self, ul=(100, 100))

# With label
SwitchOpen(parent=self, ul=(100, 100), label="SW1")
```

| Parameter         | Type  | Default | Description   |
| ----------------- | ----- | ------- | ------------- |
| `body_width`      | float | 40      | Switch width  |
| `body_height`     | float | 20      | Switch height |
| `terminal_length` | float | 10      | Lead length   |

### Junction

Filled dot indicating wire connection.

```python
Junction(parent=self, ul=(100, 100))
```

| Parameter | Type      | Default            | Description |
| --------- | --------- | ------------------ | ----------- |
| `radius`  | float     | 4                  | Dot radius  |
| `fill`    | ColorLike | `("#707070", 0.9)` | Fill color  |

---

## Styling

All elements use consistent defaults:

- Stroke: `#707070` at 90% opacity
- Stroke width: 3.0
- Fill: `#eeeeee` (gates) or none (passive components)

Override per element:

```python
AND(
    parent=self,
    ul=(100, 100),
    fill="#3498db",
    stroke=("#2c3e50", 1.0),
    stroke_width=2.0,
)
```

---

## Complete Example

```python
from od_do import cli
from od_do.diagram.base import Diagram
from diagram_libs.basic_circuit_elements import AND, OR, Buffer


class LogicDemo(Diagram):
    def draw(self):
        # Row of AND gates at different rotations
        AND(parent=self, ul=(100, 100), label="0")
        AND(parent=self, ul=(250, 100), rotation=90, label="90")
        AND(parent=self, ul=(400, 100), rotation=180, label="180")
        AND(parent=self, ul=(550, 100), rotation=270, label="270")

        # Row of OR gates
        OR(parent=self, ul=(100, 300), label="OR")
        OR(parent=self, ul=(250, 300), invert=True, label="NOR")

        # Buffers
        Buffer(parent=self, ul=(400, 300), label="BUF")
        Buffer(parent=self, ul=(550, 300), invert=True, label="NOT")


if __name__ == "__main__":
    cli()
```

Run:

```bash
python logic_demo.py --show
python logic_demo.py --padding 100  # More padding around edges
```

---

## Building Custom Components

Circuit elements are Diagram subclasses that compose od-do primitives. You can
build your own using the same pattern.

### Template

```python
from od_do.diagram.base import Diagram
from od_do import shapes, colors
from od_do.shapes import text
from od_do.paths import Line
from od_do.geometry import Point
from od_do.colors import ColorLike, Color


class MyComponent(Diagram):
    def __init__(
        self,
        stroke=("#707070", 0.9),
        stroke_width=3.0,
        label=None,
        body_width=50,
        body_height=60,
        terminal_length=10,
        **kwargs,
    ):
        # Store ALL parameters BEFORE super().__init__()
        # (super() calls draw(), so params must exist)
        self._stroke = Color.resolve_color(stroke) if stroke is not None else None
        self._stroke_width = stroke_width
        self._label = label
        self._body_width = body_width
        self._body_height = body_height
        self._terminal_length = terminal_length
        super().__init__(**kwargs)

    def draw(self):
        # Draw at origin (0, 0) - Diagram handles positioning
        shapes.Block(
            parent=self,
            ll=(0, self._body_height),
            width=self._body_width,
            height=self._body_height,
            fill=None,
            stroke=self._stroke,
            stroke_width=self._stroke_width,
        )

        # Add terminals
        Line(
            parent=self,
            start_point=(-self._terminal_length, self._body_height / 2),
            points=[f"R{self._terminal_length}"],
            width=self._stroke_width,
            color=self._stroke,
        )

    @property
    def input_pin(self):
        return Point(-self._terminal_length, self._body_height / 2)
```

### Key Rules

1. **Store params before `super().__init__()`** - The parent constructor calls
   `draw()`, so all parameters must already be set
2. **Use `**kwargs`passthrough** - Enables`parent=`, `ul=`, `rotation=`, etc.
3. **Draw at origin** - Let the Diagram placement system handle positioning
4. **Expose pins as Point properties** - For connecting wires between components

### Available Primitives

- `shapes.Block(...)`, `shapes.Circle(...)` - Basic shapes
- `shapes.OpenBlock(..., open_side="right")` - Rectangle with one side open
- `Line(parent, start_point, points, ...)` - Lines with direction strings
- `curves.SemiCircle(parent, center, radius, direction, ...)` - Half circles
- `BezierPath(parent, d="M 0,0 Q ...", ...)` - Arbitrary SVG paths
- `text.Text(parent, position, content, ...)` - Labels

---

## CLI Options

```bash
python my_circuit.py                          # Render to output/MyCircuit.svg
python my_circuit.py --show                   # Render and open viewer
python my_circuit.py --padding 100            # Custom padding (default: 50)
python my_circuit.py --output custom.svg      # Custom output path
python my_circuit.py --render-diagram "AND"   # Render only matching diagrams
```
