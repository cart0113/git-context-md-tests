# Diagram API Guide

## Core Concepts

Diagrams are Python classes. Subclass `Diagram`, override `draw()`, instantiate
shapes. Diagrams compose by nesting—pass `parent=self` to place one diagram
inside another.

### The `draw()` Method Pattern

Override `draw()` to define your shapes. No `__init__` boilerplate required.

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block, circle

class MyComponent(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=100, height=50, fill="#3498db")
        circle(parent=self, x0=80, y0=10, radius=15, fill="#e74c3c")
```

That's it! No `__init__`, no `super().__init__()` boilerplate.

### Using Your Component

```python
# As a standalone diagram
diagram = MyComponent()
diagram.render("output.svg")

# As a sub-diagram (automatically placed within parent)
MyComponent(parent=main_diagram, ul=(100, 50), rotation=45)
```

## Constructor Parameters (Set at Construction Time)

These parameters are set once when creating a diagram and control its placement
and configuration:

| Parameter         | Type          | Default | Description                                                |
| ----------------- | ------------- | ------- | ---------------------------------------------------------- |
| `parent`          | Diagram       | None    | Parent diagram. If set, this diagram becomes a sub-diagram |
| `x`               | float         | 0       | X position offset (only used when `parent` is set)         |
| `y`               | float         | 0       | Y position offset (only used when `parent` is set)         |
| `rotation`        | float         | 0       | Rotation in degrees (only used when `parent` is set)       |
| `mirror`          | str           | None    | Mirror type: `"MX"`, `"MY"`, or `"MX_MY"`                  |
| `rotation_offset` | tuple         | None    | Custom rotation pivot point as `(x, y)`                    |
| `width`           | int/float/str | "auto"  | Explicit width or `"auto"` for auto-sizing                 |
| `height`          | int/float/str | "auto"  | Explicit height or `"auto"` for auto-sizing                |
| `units`           | str           | None    | Unit system (e.g., `"px"`, `"mm"`). Inherited from parent  |
| `unit_to_pixels`  | float         | None    | Unit conversion ratio. Inherited from parent               |

## Render-Time Parameters

These parameters are set when calling `render()` or `show()`:

| Parameter        | Type  | Default | Description                                    |
| ---------------- | ----- | ------- | ---------------------------------------------- |
| `padding`        | float | 10      | Padding on all sides                           |
| `padding_left`   | float | None    | Override left padding                          |
| `padding_right`  | float | None    | Override right padding                         |
| `padding_top`    | float | None    | Override top padding                           |
| `padding_bottom` | float | None    | Override bottom padding                        |
| `backend`        | str   | None    | Force backend: `"svg"`, `"png"`, or `"drawio"` |

## Examples

### Simple Diagram

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block, circle

class SimpleDiagram(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=100, height=50, fill="#3498db")
        circle(parent=self, x0=120, y0=25, radius=25, fill="#e74c3c")

# Create and render
diagram = SimpleDiagram()
diagram.render("simple.svg", padding=20)
```

### Nested Components

```python
class LED(Diagram):
    def draw(self):
        circle(parent=self, x0=0, y0=0, radius=8, fill="#00ff00")

class LEDRow(Diagram):
    def draw(self):
        for i in range(4):
            LED(parent=self, ul=(i * 25, 0))

class LEDMatrix(Diagram):
    def draw(self):
        for j in range(4):
            LEDRow(parent=self, ul=(0, j * 25))

# Use it
diagram = LEDMatrix()
diagram.render("led_matrix.svg")
```

### Transforms

```python
class Arrow(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=50, height=20, fill="#2ecc71")
        block(parent=self, x0=40, y0=-10, width=20, height=40, fill="#2ecc71")

class TransformDemo(Diagram):
    def draw(self):
        Arrow(parent=self, ul=(50, 50))                    # Original
        Arrow(parent=self, ul=(150, 50), rotation=90)      # Rotated 90 degrees
        Arrow(parent=self, ul=(250, 50), mirror="MY")      # Mirrored horizontally
        Arrow(parent=self, ul=(350, 50), rotation=45, mirror="MX")  # Combined
```

### Custom Constructor Parameters

If you need custom parameters, set them before calling `super().__init__()`:

```python
class ColoredBox(Diagram):
    def __init__(self, color, **kwargs):
        self.color = color  # Set BEFORE super().__init__()
        super().__init__(**kwargs)

    def draw(self):
        block(parent=self, x0=0, y0=0, width=50, height=50, fill=self.color)

# Use it
ColoredBox(color="#ff0000", parent=main_diagram, ul=(100, 100))
```

## Best Practices

1. **Override `draw()`, not `__init__`** - Unless you need custom constructor
   parameters
2. **Use factory functions** - `block()`, `circle()`, `rectangle()` instead of
   raw classes
3. **Define shapes at local coordinates** - Use `x0=0, y0=0` as the origin, let
   placement handle positioning
4. **Let parent handle transforms** - Don't bake rotation/mirror into your
   shapes
5. **Keep components small and focused** - Compose complex diagrams from simple
   components
