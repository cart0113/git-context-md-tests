# Shapes

Shapes are the fundamental drawing primitives in OD-DO. Every shape has a
bounding box, anchor points, and styling options.

## Point Inputs

**Important:** Anywhere a `Point` is accepted as input, you can also pass a
2-tuple of numbers `(x, y)`. This applies to all positioning parameters (`ll`,
`ul`, `lr`, `ur`, `center`) and when using shape anchor points.

```python
from od_do import Point
from od_do.shapes import Block

# These are equivalent:
Block(parent=self, ll=(100, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)
Block(parent=self, ll=Point(100, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Shape anchor points (via .points) return Point objects, which work directly:
block1 = Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)
Block(parent=self, ur=block1.points.ll, width=80, height=40, fill=None, stroke=None, stroke_width=1)
```

## Creating Shapes

### Block (Rectangle)

```python
from od_do import colors
from od_do.shapes import Block

# Position by lower-left corner
block = Block(
    parent=self,
    ll=(100, 200),
    width=150,
    height=80,
    fill=colors.RED,
    stroke=colors.BLACK,
    stroke_width=2,
)

# Position by upper-left corner
block = Block(parent=self, ul=(100, 100), width=150, height=80, fill=None, stroke=None, stroke_width=1)

# Position by upper-right corner
block = Block(parent=self, ur=(250, 100), width=150, height=80, fill=None, stroke=None, stroke_width=1)

# Position by lower-right corner
block = Block(parent=self, lr=(250, 200), width=150, height=80, fill=None, stroke=None, stroke_width=1)
```

### Rectangle

`Rectangle` is identical to `Block`, just a different name:

```python
from od_do.shapes import Rectangle

rect = Rectangle(
    parent=self,
    ll=(100, 200),
    width=150,
    height=80,
    fill=colors.BLUE,
    stroke=None,
    stroke_width=1,
)
```

### Circle

```python
from od_do.shapes import Circle

# Position by center point (most common)
circle = Circle(
    parent=self,
    center=(200, 150),
    radius=50,
    fill=colors.GREEN,
    stroke=colors.DARK_GREEN,
    stroke_width=2,
)

# Position by bounding box corners
circle = Circle(parent=self, ll=(150, 200), radius=50, fill=None, stroke=None, stroke_width=1)
circle = Circle(parent=self, ul=(150, 100), radius=50, fill=None, stroke=None, stroke_width=1)
```

## Positioning Options

All shapes support positioning by any corner. Specify at most one (if none
specified, defaults to `ll=(0, 0)`):

| Parameter | Description                                   |
| --------- | --------------------------------------------- |
| `ll`      | Lower-left corner (default if none specified) |
| `ul`      | Upper-left corner                             |
| `lr`      | Lower-right corner                            |
| `ur`      | Upper-right corner                            |
| `center`  | Center point (circles only)                   |

```python
from od_do.shapes import Block, Circle

# Default position at origin
Block(parent=self, width=100, height=50, fill=None, stroke=None, stroke_width=1)  # ll=(0, 0)

# Explicit positioning
Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)
Block(parent=self, ur=(300, 100), width=100, height=50, fill=None, stroke=None, stroke_width=1)
```

### Using Point Objects

You can use `Point` objects or tuples:

```python
from od_do import Point
from od_do.shapes import Block

# Using tuple
Block(parent=self, ll=(100, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Using Point
Block(parent=self, ll=Point(100, 200), width=50, height=30, fill=None, stroke=None, stroke_width=1)

# Using another shape's anchor point
block1 = Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)
Block(parent=self, ur=block1.points.ll, width=80, height=40, fill=None, stroke=None, stroke_width=1)
```

## Anchor Points

Every shape provides anchor points via the `.points` property for connecting to
other shapes:

### Corner Points

```python
from od_do.shapes import Block

block = Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)

# Access corners via .points
block.points.ll      # Lower-left: Point(100, 200)
block.points.ul      # Upper-left: Point(100, 150)
block.points.lr      # Lower-right: Point(200, 200)
block.points.ur      # Upper-right: Point(200, 150)
block.points.center  # Center: Point(150, 175)
```

### Edge Interpolation

The `points` property also provides edge interpolation (0.0 to 1.0):

```python
block.points.left(0.0)    # Same as ll
block.points.left(0.5)    # Midpoint of left edge
block.points.left(1.0)    # Same as ul

block.points.right(0.0)   # Same as lr
block.points.right(0.5)   # Midpoint of right edge
block.points.right(1.0)   # Same as ur

block.points.top(0.0)     # Same as ul
block.points.top(0.5)     # Midpoint of top edge
block.points.top(1.0)     # Same as ur

block.points.bottom(0.0)  # Same as ll
block.points.bottom(0.5)  # Midpoint of bottom edge
block.points.bottom(1.0)  # Same as lr
```

## Bounding Box

Every shape has a bounding box:

```python
from od_do.shapes import Block

block = Block(parent=self, ll=(100, 200), width=100, height=50, fill=None, stroke=None, stroke_width=1)

# Access bounding box
bbox = block.bbox
print(bbox.ll)     # Point(100, 200)
print(bbox.ur)     # Point(200, 150)
print(bbox.width)  # 100
print(bbox.height) # 50
print(bbox.center) # Point(150, 175)
```

## Styling Options

| Parameter      | Type         | Description                                       |
| -------------- | ------------ | ------------------------------------------------- |
| `fill`         | str or Color | Fill color (hex string or Color object)           |
| `stroke`       | str or Color | Stroke color                                      |
| `stroke_width` | float        | Width of the stroke                               |
| `corners`      | str          | Rounded corners for rectangles/blocks (see below) |

```python
from od_do.shapes import Block

# Using hex strings
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill="#ff6b6b", stroke="#000000", stroke_width=2)

# Using Color objects
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=colors.RED, stroke=colors.BLACK, stroke_width=2)

# With transparency
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=colors.BLUE.alpha(0.5), stroke=colors.DARK_BLUE, stroke_width=1)

# No fill (outline only)
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=None, stroke=colors.BLACK, stroke_width=2)
```

## Rounded Corners

Blocks and rectangles support rounded corners via the `corners` parameter. The
corner radius is calculated as a fraction of the smaller dimension (width or
height).

### Preset Values

| Value              | Radius | Description         |
| ------------------ | ------ | ------------------- |
| `"slightly-round"` | 5%     | Subtle rounding     |
| `"round"`          | 10%    | Standard rounding   |
| `"very-round"`     | 20%    | Pronounced rounding |

```python
from od_do.shapes import Block, Rectangle

# Standard rounded corners
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=colors.BLUE, stroke=None, stroke_width=1, corners="round")

# Very rounded (almost pill-shaped for wide rectangles)
Block(parent=self, ll=(100, 200), width=200, height=50,
      fill=colors.GREEN, stroke=None, stroke_width=1, corners="very-round")

# Subtle rounding
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=colors.RED, stroke=None, stroke_width=1, corners="slightly-round")
```

### Custom Values

Use `"round:<factor>"` for custom rounding where factor is 0.0 to 1.0:

```python
# 30% of min dimension
Block(parent=self, ll=(100, 200), width=100, height=50,
      fill=colors.PURPLE, stroke=None, stroke_width=1, corners="round:0.3")

# 50% creates a pill shape when width >> height
Rectangle(parent=self, ll=(100, 200), width=200, height=40,
          fill=colors.ORANGE, stroke=None, stroke_width=1, corners="round:0.5")
```

### Corner Radius Calculation

The corner radius is calculated as:

```
radius = min(width, height) * factor
```

For a 100x50 block:

- `"slightly-round"` → radius = 50 \* 0.05 = 2.5
- `"round"` → radius = 50 \* 0.1 = 5
- `"very-round"` → radius = 50 \* 0.2 = 10
- `"round:0.5"` → radius = 50 \* 0.5 = 25

## Connecting Shapes

Use anchor points to connect shapes together:

```python
from od_do.shapes import Block, Circle

class ConnectedDiagram(diagram.Diagram):
    def draw(self):
        # First block
        block1 = Block(
            parent=self,
            ll=(100, 200),
            width=100,
            height=50,
            fill=colors.LIGHT_BLUE,
            stroke=None,
            stroke_width=1,
        )

        # Second block attached to first (ur at first's ll)
        block2 = Block(
            parent=self,
            ur=block1.points.ll,
            width=80,
            height=40,
            fill=colors.LIGHT_GREEN,
            stroke=None,
            stroke_width=1,
        )

        # Third block attached to first (ul at first's ur)
        block3 = Block(
            parent=self,
            ul=block1.points.ur,
            width=80,
            height=40,
            fill=colors.LIGHT_YELLOW,
            stroke=None,
            stroke_width=1,
        )

        # Circle centered on first block's right edge midpoint
        Circle(
            parent=self,
            center=block1.points.right(0.5),
            radius=15,
            fill=colors.RED,
            stroke=None,
            stroke_width=1,
        )
```

## Coordinate System

OD-DO uses SVG coordinates where:

- X increases to the right
- Y increases downward
- (0, 0) is at the top-left

This means:

- `ul` (upper-left) has the smallest Y value
- `ll` (lower-left) has the largest Y value
- `ur` (upper-right) has the largest X value
