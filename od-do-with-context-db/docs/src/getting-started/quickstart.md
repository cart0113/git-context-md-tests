# Quick Start

od-do diagrams are Python objects. You define a diagram by subclassing `Diagram`
and overriding `draw()` to instantiate shapes. Diagrams nest inside other
diagrams via `parent=self`, forming a tree that renders to SVG, PNG, or Draw.io.

## Creating a Simple Diagram

```python
from od_do import diagram, colors
from od_do.shapes import Block, Circle

class MyDiagram(diagram.Diagram):
    def draw(self):
        # Add a block positioned by its lower-left corner
        Block(
            parent=self,
            ll=(100, 200),
            width=200,
            height=100,
            fill=colors.RED,
            stroke=colors.BLACK,
            stroke_width=1,
        )

        # Add a circle positioned by its center
        Circle(
            parent=self,
            center=(400, 150),
            radius=50,
            fill=colors.BLUE,
            stroke=colors.BLACK,
            stroke_width=1,
        )

# Create and render the diagram
my_diag = MyDiagram()
my_diag.render('output.svg')
```

## Positioning Shapes

Shapes can be positioned using any corner:

```python
from od_do.shapes import Block, Circle

# Position by lower-left corner (default for most use cases)
Block(parent=self, ll=(100, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Position by upper-left corner
Block(parent=self, ul=(100, 100), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Position by upper-right corner
Block(parent=self, ur=(200, 100), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Position by lower-right corner
Block(parent=self, lr=(200, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Position circles by center
Circle(parent=self, center=(150, 150), radius=25, fill=None, stroke=None, stroke_width=1)
```

## Using Anchor Points

Every shape has anchor points accessible via `.points` that you can use to
position other shapes:

```python
from od_do.shapes import Block

class ConnectedDiagram(diagram.Diagram):
    def draw(self):
        # Create a block
        block1 = Block(
            parent=self,
            ll=(100, 200),
            width=100,
            height=50,
            fill=colors.LIGHT_BLUE,
            stroke=None,
            stroke_width=1,
        )

        # Position another shape relative to the first
        Block(
            parent=self,
            ur=block1.points.ll,  # Upper-right corner at block1's lower-left
            width=80,
            height=40,
            fill=colors.LIGHT_GREEN,
            stroke=None,
            stroke_width=1,
        )

        # Access corners and edge midpoints
        lower_left = block1.points.ll        # Corner point
        mid_left = block1.points.left(0.5)   # Midpoint of left edge
        mid_top = block1.points.top(0.5)     # Midpoint of top edge
```

## Drawing Paths

Draw lines between points using absolute coordinates or direction strings:

```python
from od_do import paths
from od_do.shapes import Block

class PathDiagram(diagram.Diagram):
    def draw(self):
        block1 = Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)

        # Line with direction strings: Down 20, Right 30, Up 10
        paths.line(
            parent=self,
            start=block1.points.ll,
            points=["D20", "R30", "U10"],
            width=2,
            color=colors.DARK_RED,
        )

        # Line with absolute coordinates
        paths.line(
            parent=self,
            start=(50, 50),
            points=[(100, 50), (100, 100), (150, 100)],
            width=2,
            color=colors.BLUE,
        )
```

Direction strings:

- `U20`: Up 20 units
- `D20`: Down 20 units
- `L20`: Left 20 units
- `R20`: Right 20 units
- `D10:R10`: Combined diagonal (down 10 AND right 10)

## Using Colors

OD-DO provides a comprehensive color system:

```python
from od_do import colors
from od_do.shapes import Block

# Use predefined colors
fill = colors.RED
stroke = colors.DARK_BLUE

# Manipulate colors
lighter = colors.RED.lighten(0.3)        # 30% lighter
darker = colors.BLUE.darken(0.2)         # 20% darker
transparent = colors.GREEN.alpha(0.5)    # 50% transparent
mixed = colors.RED.blend(colors.BLUE, 0.5)  # 50/50 mix

# Use in shapes
Block(
    parent=self,
    ll=(100, 100),
    width=100,
    height=50,
    fill=colors.LIGHT_BLUE.alpha(0.7),
    stroke=colors.DARK_BLUE,
    stroke_width=1,
)
```

## Setting Units and Scale

Define custom units at the class level:

```python
from od_do.shapes import Block

class MicroDiagram(diagram.Diagram):
    units = "um"           # Micrometers
    unit_to_pixels = 40    # 1 um = 40 pixels

    def draw(self):
        # Coordinates are now in micrometers
        Block(parent=self, ll=(10, 20), width=5, height=3, fill=None, stroke=None, stroke_width=1)
```

## Using Different Backends

### SVG Backend

```python
diagram.render('output.svg', backend='svg')
```

### PNG Backend

```python
diagram.render('output.png', backend='png')
```

### Draw.io Backend

```python
diagram.render('output.drawio', backend='drawio')
```

## Using the CLI

Add the CLI to your diagram file:

```python
from od_do import cli

# ... diagram class definitions ...

if __name__ == "__main__":
    cli()
```

Then run:

```bash
# Render to output/<DiagramName>.svg
python my_diagram.py

# Render and open in viewer
python my_diagram.py --show

# Custom padding (default: 50px)
python my_diagram.py --padding 100

# Custom output path
python my_diagram.py --output diagram.svg
```

### Multiple Diagrams

When a file contains multiple diagram classes, the CLI renders the **last
diagram** defined in the file by default. This allows you to define
helper/component diagrams first and your main diagram last.

```bash
# Renders the last diagram in the file
python my_diagram.py

# List all diagrams in the file (in source order)
python my_diagram.py --list-diagrams
```

The `--render-diagram` option accepts a regex pattern (case-insensitive) to
render specific diagrams:

```bash
# Render specific diagram
python my_diagram.py --render-diagram MyDiagram

# Render all diagrams containing "Circuit"
python my_diagram.py --render-diagram circuit

# Render diagrams starting with "Simple"
python my_diagram.py --render-diagram '^simple'

# Render all diagrams
python my_diagram.py --render-diagram '.*'
```

If the pattern doesn't match any diagram, the CLI displays valid diagram names.

### Debugging with Rulers and Grids

Show rulers on the outside of the diagram displaying coordinates in both drawing
units and pixels:

```bash
python my_diagram.py --show-ruler --show
```

Show a light grey grid overlay on the diagram:

```bash
python my_diagram.py --show-grid --show
```

Combine both for precise positioning work:

```bash
python my_diagram.py --show-ruler --show-grid --show
```

### All CLI Options

```bash
python my_diagram.py --help

Options:
  --render-diagram TEXT    Name or regex pattern of diagram class(es)
  --list-diagrams          List all diagram classes in the file and exit
  --kwarg TEXT             Keyword arguments in format key=value (multiple)
  --show-ruler             Show ruler on the outside of the diagram
  --show-grid              Show grid overlay on the diagram
  --output TEXT            Output file path
  --backend [svg|png|drawio]  Backend to use (default: svg)
  --show                   Open the diagram in viewer
  --padding FLOAT          Padding around diagram in pixels (default: 50)
```
