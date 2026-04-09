# Paths

Paths are connected sequences of points that form lines. OD-DO supports both
absolute coordinates and direction strings for flexible path creation.

## BezierPath

For arbitrary curved shapes, use `BezierPath` which accepts SVG path data:

```python
from od_do.shapes.curves import BezierPath

# Quadratic bezier curve (Q command)
BezierPath(
    parent=self,
    d="M 0,0 Q 25,50 50,0",  # Start, control point, end
    stroke=colors.BLUE,
    stroke_width=2,
    fill=None,
)

# Closed shape with curves
BezierPath(
    parent=self,
    d="M 0,0 Q 10,30 0,60 Q 40,60 60,30 Q 40,0 0,0 Z",
    fill=colors.LIGHT_BLUE,
    stroke=colors.DARK_BLUE,
    stroke_width=2,
)
```

Supported SVG path commands:

- `M x,y` - Move to
- `L x,y` - Line to
- `Q cx,cy x,y` - Quadratic bezier (one control point)
- `C c1x,c1y c2x,c2y x,y` - Cubic bezier (two control points)
- `A rx,ry rotation large-arc,sweep x,y` - Arc
- `Z` - Close path

---

## Point Inputs

**Important:** Anywhere a `Point` is accepted as input (such as `start_point` or
relative coordinate points in the `points` list), you can also pass a 2-tuple of
numbers `(x, y)`. Shape anchor points (accessed via `block.points.ll`) return
`Point` objects that work directly.

**Important:** All coordinate tuples in the `points` list are RELATIVE to
`start_point`. A point like `(50, 30)` means "50 units right, 30 units down from
start_point".

## Creating Lines

### Basic Line

```python
from od_do.paths import Line
from od_do import colors

# Line with relative coordinates (relative to start_point)
line = Line(
    parent=self,
    start_point=(100, 100),
    points=[(100, 0), (100, 100), (0, 100)],  # Offsets from start_point
    width=2,
    color=colors.BLUE,
)
```

### Line with Direction Strings

Direction strings provide a convenient way to specify relative movements:

```python
# Line that goes: Down 50, Right 100, Up 25
line = Line(
    parent=self,
    start_point=(100, 100),
    points=["D50", "R100", "U25"],
    width=2,
    color=colors.RED,
)
```

## Direction String Format

### Single Directions

| String | Direction | Movement          |
| ------ | --------- | ----------------- |
| `U20`  | Up        | Y decreases by 20 |
| `D20`  | Down      | Y increases by 20 |
| `L20`  | Left      | X decreases by 20 |
| `R20`  | Right     | X increases by 20 |

Direction strings are case-insensitive (`u20` works the same as `U20`).

Decimal values are supported: `D10.5`, `R33.33`

### Combined Directions (Diagonal Movement)

Use a colon to combine two directions for diagonal movement:

| String    | Movement                        |
| --------- | ------------------------------- |
| `D10:R10` | Down 10 AND right 10 (diagonal) |
| `U20:L15` | Up 20 AND left 15 (diagonal)    |
| `R50:D25` | Right 50 AND down 25 (diagonal) |

Combined directions must pair one vertical (U/D) with one horizontal (L/R)
direction.

```python
# Line with diagonal segment at the end
line = Line(
    parent=self,
    start_point=block.points.lr,
    points=["R100", "D100", "R100", "D10:R10"],  # Last segment is diagonal
    width=2,
    color=colors.DARK_GRAY,
)
```

## Mixed Coordinates

You can mix relative coordinates and direction strings:

```python
line = Line(
    parent=self,
    start_point=(50, 50),
    points=[
        (50, 0),          # Relative to start: (100, 50)
        "D30",            # Direction: down 30 from previous
        (100, 30),        # Relative to start: (150, 80)
        "R20",            # Direction: right 20 from previous
    ],
    width=2,
    color=colors.DARK_GREEN,
)
```

## Starting from Shape Anchor Points

A common pattern is to start lines from shape anchor points:

```python
from od_do.paths import Line
from od_do.shapes import Block

class WiredDiagram(diagram.Diagram):
    def draw(self):
        # Create blocks
        block1 = Block(parent=self, ll=(100, 200), width=100, height=50)
        block2 = Block(parent=self, ll=(300, 200), width=100, height=50)

        # Connect from block1's right edge to block2's left edge
        Line(
            parent=self,
            start_point=block1.points.right(0.5),  # Middle of right edge
            points=[
                "R20",                         # Out from block1
                block2.points.left(0.5),       # To middle of block2's left edge
            ],
            width=2,
            color=colors.DARK_BLUE,
        )

        # Wire from block1's bottom
        Line(
            parent=self,
            start_point=block1.points.ll,
            points=["D30", "R200", "U30"],
            width=2,
            color=colors.DARK_RED,
        )
```

## Styling Options

| Parameter      | Type         | Description                                                            |
| -------------- | ------------ | ---------------------------------------------------------------------- |
| `width`        | float        | Stroke width (default: 1)                                              |
| `color`        | str or Color | Line color (hex string or Color object)                                |
| `line_style`   | str or tuple | Line pattern: "solid", "dashed", "dotted", "dash_dot", or custom tuple |
| `start_marker` | Marker       | Marker at the start of the line                                        |
| `end_marker`   | Marker       | Marker at the end of the line                                          |

```python
# Using hex string
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, color="#FF0000")

# Using Color object
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, color=colors.RED)

# With transparency
Line(parent=self, start_point=(0, 0), points=["R100"], width=3,
     color=colors.BLUE.alpha(0.5))
```

## Line Styles

Lines support various dash patterns:

```python
from od_do.paths import Line

# Predefined styles
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, line_style="dashed")
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, line_style="dotted")
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, line_style="dash_dot")

# Custom pattern (dash, gap, dash, gap, ...)
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, line_style=(15, 5, 5, 5))
```

Available line styles:

- `"solid"` (default)
- `"dashed"`
- `"dotted"`
- `"dash_dot"`
- `"dash_dot_dot"`
- `"long_dash"`
- `"short_dash"`

## Line Markers

Markers are decorative elements at line endpoints (arrows, circles, squares,
etc.).

```python
from od_do import Arrow, Circle, Square, Diamond, Bar
from od_do.paths import Line

# Arrow at end
Line(
    parent=self,
    start_point=(100, 100),
    points=["R200"],
    width=2,
    color=colors.DARK_BLUE,
    end_marker=Arrow(),
)

# Bidirectional arrow
Line(
    parent=self,
    start_point=(100, 100),
    points=["R200"],
    width=2,
    color=colors.DARK_RED,
    start_marker=Arrow(),
    end_marker=Arrow(),
)

# Different marker types
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, end_marker=Circle())
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, end_marker=Square())
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, end_marker=Diamond())
Line(parent=self, start_point=(0, 0), points=["R100"], width=2, end_marker=Bar())
```

### Marker Size

The `size` parameter controls marker width. Named sizes scale with line width:

| Size                 | Multiplier     |
| -------------------- | -------------- |
| `"very-small"`       | 2× line width  |
| `"small"`            | 3× line width  |
| `"medium"` (default) | 5× line width  |
| `"large"`            | 7× line width  |
| `"very-large"`       | 10× line width |

```python
Arrow(size="small")      # Scales with line width
Arrow(size="large")      # Larger, still scales
Arrow(size=15)           # Absolute size in user units
```

### Marker Length

The `length` parameter controls how pointy/long the arrow is:

| Length               | Multiplier |
| -------------------- | ---------- |
| `"very-short"`       | 0.4×       |
| `"short"`            | 0.6×       |
| `"medium"` (default) | 1.0×       |
| `"tall"`             | 1.4×       |
| `"very-tall"`        | 2.0×       |

```python
Arrow(length="short")    # Stubby arrow
Arrow(length="tall")     # Long, pointy arrow
Arrow(length=1.5)        # Custom multiplier
```

### Marker Color

By default, markers inherit the line's color. Override with `color`:

```python
# Inherits line color (including transparency)
Line(
    parent=self,
    start_point=(0, 0),
    points=["R100"],
    width=2,
    color=colors.DARK_GRAY.alpha(0.5),
    end_marker=Arrow(),
)

# Custom marker color
Line(
    parent=self,
    start_point=(0, 0),
    points=["R100"],
    width=2,
    color=colors.DARK_BLUE,
    end_marker=Arrow(color=colors.RED),
)
```

### Arrow Styles

Arrows support different styles:

```python
Arrow(style="closed")    # Solid filled triangle (default)
Arrow(style="open")      # Open chevron outline
Arrow(style="barbed")    # Barbed/notched arrowhead
```

### Inverted Arrows

Use `invert=True` to create arrows that point inward (into the line) instead of
outward. This is useful for indicating endpoints or terminations:

```python
# Arrow pointing into the line at the end
Line(
    parent=self,
    start_point=(100, 100),
    points=["R200"],
    width=2,
    color=colors.DARK_GRAY,
    end_marker=Arrow(invert=True),
)

# Square at start, inverted arrow at end
Line(
    parent=self,
    start_point=block.points.lr,
    points=["R100", "D50"],
    width=1,
    color=colors.GRAY,
    start_marker=Square(size="medium"),
    end_marker=Arrow(size="medium", invert=True),
)
```

Inverted arrows render as trapezoids with a flat edge matching the line width,
creating a clean termination point.

### Filled vs Outline

For Circle, Square, and Diamond markers:

```python
Circle(filled=True)      # Solid fill (default)
Circle(filled=False)     # Outline only
```

## StrokeLine

`StrokeLine` is a specialized line type that renders with colored edges
(strokes) along the parallel sides of the line, with a different fill color in
the center. This is useful for creating lines that look like bordered paths or
channels.

```python
from od_do.paths import StrokeLine
from od_do import colors

# Line with blue edges and red fill
line = StrokeLine(
    parent=self,
    start_point=(100, 100),
    points=["D50", "R30", "D50"],
    width=20,                           # Total line width
    color=colors.RED.alpha(0.5),        # Fill color (center)
    stroke_color=colors.BLUE.alpha(0.5),# Edge color (sides)
    stroke_width=3,                     # Edge stroke width
)
```

### StrokeLine Parameters

| Parameter      | Type         | Description                                           |
| -------------- | ------------ | ----------------------------------------------------- |
| `width`        | float        | Total width of the line (must be >= 2 × stroke_width) |
| `color`        | str or Color | Fill color for the center of the line                 |
| `stroke_color` | str or Color | Color for the edge strokes                            |
| `stroke_width` | float        | Width of each edge stroke (default: 1)                |
| `line_style`   | str or tuple | Optional dash pattern                                 |

### How StrokeLine Works

The line is rendered as three separate polylines:

- Two edge strokes offset to the left and right of the center path
- One center fill at the remaining width

This approach ensures that semi-transparent colors don't mix where edges meet
the fill.

### Constraints

- `width` must be at least `2 × stroke_width` to leave room for the fill
- Markers are not supported on StrokeLine (use regular Line for markers)

```python
# This will raise ValueError - width too small
StrokeLine(
    parent=self,
    start_point=(0, 0),
    points=["R100"],
    width=4,
    stroke_width=3,  # Error: 4 < 2*3
    color=colors.RED,
    stroke_color=colors.BLUE,
)
```

## Path Properties

Lines have bounding boxes and anchor points:

```python
line = Line(parent=self, start_point=(100, 100), points=["R100", "D50"])

# Access all points
print(line.all_points)  # [Point(100, 100), Point(200, 100), Point(200, 150)]

# Bounding box
print(line.bbox.ll)     # Point(100, 150)
print(line.bbox.ur)     # Point(200, 100)
```

## Common Patterns

### Orthogonal Routing

Create Manhattan-style (right-angle only) routing:

```python
# Route around an obstacle
Line(
    parent=self,
    start_point=block1.points.ur,
    points=["U20", "R150", "D70"],
    width=2,
    color=colors.BLUE,
)
```

### Connecting Multiple Blocks

```python
from od_do.shapes import Block

class MultiConnectionDiagram(diagram.Diagram):
    def draw(self):
        blocks = []
        for i in range(3):
            blocks.append(Block(
                parent=self,
                ll=(100 + i * 150, 200),
                width=100,
                height=50,
                fill=colors.LIGHT_BLUE,
            ))

        # Connect blocks in series
        for i in range(len(blocks) - 1):
            Line(
                parent=self,
                start_point=blocks[i].points.right(0.5),
                points=[blocks[i + 1].points.left(0.5)],
                width=2,
                color=colors.DARK_BLUE,
            )
```

### Signal Traces

For circuit-like diagrams:

```python
# Multiple parallel traces
for i, color in enumerate([colors.RED, colors.BLUE, colors.GREEN]):
    Line(
        parent=self,
        start_point=(50, 100 + i * 5),
        points=["R200"],
        width=1,
        color=color,
    )
```

## Coordinate System

Paths use the same SVG coordinate system as shapes:

- X increases to the right
- Y increases downward
- `U` (up) decreases Y
- `D` (down) increases Y
- `L` (left) decreases X
- `R` (right) increases X

## Point Validation

Points are validated when the line is created. If a point has an invalid format,
you'll get a clear error message:

```python
# Invalid: missing number after direction
Line(parent=self, start_point=(0, 0), points=["D"])
# ValueError: Invalid direction string at index 0: 'D'.
# Expected single direction like 'U20', 'D10', 'L5', 'R30'
# or combined diagonal like 'D10:R10'.

# Invalid: combining two vertical directions
Line(parent=self, start_point=(0, 0), points=["D10:U10"])
# ValueError: Invalid combined direction at index 0: 'D10:U10'.
# Cannot combine two vertical directions (U/D).
# Use one vertical and one horizontal, e.g., 'D10:R10'.

# Invalid: wrong tuple size
Line(parent=self, start_point=(0, 0), points=[(10, 20, 30)])
# ValueError: Invalid coordinate tuple at index 0: (10, 20, 30).
# Expected a 2-tuple like (x, y), got 3 elements.
```

Valid point formats:

- **Tuples**: `(x, y)` - relative offset from start_point
- **Point objects**: `block.points.ll` - shape anchor points
- **Single directions**: `"U20"`, `"D10"`, `"L5"`, `"R30"`
- **Combined directions**: `"D10:R10"`, `"U5:L15"` (one vertical + one
  horizontal)
