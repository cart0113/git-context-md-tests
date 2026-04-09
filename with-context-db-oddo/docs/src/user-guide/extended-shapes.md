# Extended Shapes

Beyond the basic `block`, `rectangle`, and `circle`, OD-DO provides extended
shape modules for curves, polygons, flowchart shapes, annotations, and ellipses.

## Importing Extended Shapes

```python
from od_do.shapes import curves, polygon, annotations, flowchart
from od_do.shapes.ellipse import Ellipse
```

---

## Curves

The `curves` module provides Bezier curves, arcs, and semi-circles.

### Quadratic Bezier Curve

A curve with one control point. The curve starts at `start`, bends toward
`control`, and ends at `end`.

```python
from od_do.shapes import curves

curves.QuadraticBezier(
    parent=self,
    start=(100, 200),      # Starting point
    control=(150, 100),    # Control point (curve bends toward this)
    end=(200, 200),        # Ending point
    stroke=colors.BLUE,
    stroke_width=2,
    fill=None,             # Optional fill (closes the curve)
)
```

### Cubic Bezier Curve

A curve with two control points for more complex curves.

```python
curves.CubicBezier(
    parent=self,
    start=(100, 200),
    control1=(130, 100),   # First control point
    control2=(170, 100),   # Second control point
    end=(200, 200),
    stroke=colors.RED,
    stroke_width=2,
)
```

### Arc

A partial circle or ellipse. Angles are in degrees, with 0° at 3 o'clock (right
side) and increasing counter-clockwise.

```python
# Circular arc
curves.Arc(
    parent=self,
    center=(200, 200),
    radius=50,
    start_angle=0,         # Start at 3 o'clock
    end_angle=270,         # End at 6 o'clock (270° counter-clockwise)
    stroke=colors.GREEN,
    stroke_width=2,
)

# Elliptical arc
curves.Arc(
    parent=self,
    center=(200, 200),
    radius=60,             # X radius
    radius_y=30,           # Y radius (elliptical)
    start_angle=30,
    end_angle=150,
    stroke=colors.PURPLE,
    stroke_width=2,
)
```

### Semi-Circle

A half circle in one of four directions.

```python
# Semi-circle bulging upward
curves.SemiCircle(
    parent=self,
    center=(100, 200),     # Center of the flat edge
    radius=40,
    direction="up",        # "up", "down", "left", or "right"
    stroke=colors.BLUE,
    fill=colors.LIGHT_BLUE,
    stroke_width=2,
)
```

| Direction | Description                        |
| --------- | ---------------------------------- |
| `"up"`    | Flat edge at bottom, bulge upward  |
| `"down"`  | Flat edge at top, bulge downward   |
| `"left"`  | Flat edge at right, bulge leftward |
| `"right"` | Flat edge at left, bulge rightward |

---

## Polygons

The `polygon` module provides regular polygons and stars.

### Regular Polygons

All regular polygons are defined by `center`, `radius` (circumradius), and
optionally `rotation` (degrees).

```python
from od_do.shapes import polygon

# Triangle (3 sides) - vertex points up by default
polygon.Triangle(
    parent=self,
    center=(100, 100),
    radius=50,
    fill=colors.LIGHT_RED,
    stroke=colors.DARK_RED,
    stroke_width=2,
    rotation=0,            # Optional: rotate the polygon
)

# Pentagon (5 sides)
polygon.Pentagon(
    parent=self,
    center=(200, 100),
    radius=50,
    fill=colors.LIGHT_BLUE,
    stroke=colors.DARK_BLUE,
)

# Hexagon (6 sides) - flat top by default (rotation=30)
polygon.Hexagon(
    parent=self,
    center=(300, 100),
    radius=50,
    fill=colors.LIGHT_GREEN,
    stroke=colors.DARK_GREEN,
    rotation=30,           # Default: flat top. Use 0 for pointy top
)

# Octagon (8 sides)
polygon.Octagon(
    parent=self,
    center=(400, 100),
    radius=50,
    fill=colors.LIGHT_YELLOW,
    stroke=colors.GOLD,
)

# Any regular polygon (e.g., 12 sides)
polygon.RegularPolygon(
    parent=self,
    center=(500, 100),
    radius=50,
    sides=12,
    fill=colors.LIGHT_PURPLE,
    stroke=colors.PURPLE,
)
```

### Star

A star shape with customizable number of points, outer radius (tips), and inner
radius (valleys).

```python
# 5-pointed star
polygon.Star(
    parent=self,
    center=(100, 200),
    outer_radius=50,       # Radius to star tips
    inner_radius=20,       # Radius to inner valleys
    num_points=5,
    fill=colors.GOLD,
    stroke=colors.DARK_ORANGE,
    stroke_width=2,
    rotation=0,            # Optional rotation
)

# 6-pointed star (Star of David shape)
polygon.Star(
    parent=self,
    center=(200, 200),
    outer_radius=50,
    inner_radius=30,
    num_points=6,
    fill=colors.MD_CYAN,
    stroke=colors.TEAL,
)
```

---

## Ellipse

An ellipse with independent X and Y radii. Unlike `circle` which has equal
radii.

```python
from od_do.shapes.ellipse import Ellipse

# Wide ellipse
Ellipse(
    parent=self,
    center=(200, 150),
    radius_x=80,           # Horizontal radius
    radius_y=40,           # Vertical radius
    fill=colors.LIGHT_BLUE,
    stroke=colors.DARK_BLUE,
    stroke_width=2,
)

# Tall ellipse
Ellipse(
    parent=self,
    center=(350, 150),
    radius_x=30,
    radius_y=60,
    fill=colors.LIGHT_GREEN,
    stroke=colors.DARK_GREEN,
)
```

---

## Flowchart Shapes

The `flowchart` module provides common shapes for flowcharts, architecture
diagrams, and technical drawings.

### Diamond

Decision shape (rhombus) for flowcharts.

```python
from od_do.shapes import flowchart

flowchart.Diamond(
    parent=self,
    center=(200, 200),
    width=100,
    height=70,
    fill=colors.LIGHT_YELLOW,
    stroke=colors.GOLD,
    stroke_width=2,
)
```

### Parallelogram

Data/IO shape for flowcharts. The `slant` parameter controls the horizontal
offset of the top edge.

```python
flowchart.Parallelogram(
    parent=self,
    ll=(100, 200),         # Lower-left corner
    width=120,
    height=60,
    slant=25,              # Optional: horizontal offset (default: 20% of width)
    fill=colors.LIGHT_BLUE,
    stroke=colors.DARK_BLUE,
)
```

### Document

A document shape with a wavy bottom edge.

```python
flowchart.Document(
    parent=self,
    ll=(100, 200),
    width=100,
    height=70,
    wave_height=10,        # Optional: height of the wave (default: 10% of height)
    fill=colors.WHITE,
    stroke=colors.BLACK,
)
```

### Cylinder

A 3D cylinder for database icons.

```python
flowchart.Cylinder(
    parent=self,
    center=(200, 200),
    width=80,              # Diameter
    height=100,            # Body height
    ellipse_ratio=0.2,     # Optional: ellipse height as ratio of width
    fill=colors.LIGHT_GRAY,
    stroke=colors.DARK_GRAY,
)
```

### Cloud

A cloud shape for cloud services, thoughts, or grouping.

```python
flowchart.Cloud(
    parent=self,
    center=(200, 200),
    width=120,
    height=80,
    fill=colors.MD_CYAN,
    stroke=colors.TEAL,
)
```

### Terminator

A stadium/pill shape for start/end in flowcharts. Has fully rounded ends.

```python
flowchart.Terminator(
    parent=self,
    ll=(100, 200),
    width=120,
    height=50,
    fill=colors.LIGHT_GREEN,
    stroke=colors.DARK_GREEN,
)
```

---

## Annotations

The `annotations` module provides shapes for technical drawings and annotations.

### Dimension Line

A measurement line with extension lines and tick marks for technical drawings.

```python
from od_do.shapes import annotations

annotations.DimensionLine(
    parent=self,
    start=(100, 200),      # First measurement point
    end=(300, 200),        # Second measurement point
    offset=25,             # Distance of dimension line from points
    extension=5,           # How far extension lines extend past dimension line
    tick_size=6,           # Size of tick marks
    stroke=colors.BLACK,
    stroke_width=1,
)

# Vertical dimension line
annotations.DimensionLine(
    parent=self,
    start=(100, 100),
    end=(100, 200),
    offset=-25,            # Negative offset puts line on left side
    stroke=colors.BLACK,
)
```

### Leader Line

An arrow line with optional elbow for annotations. Points from a target to a
label position.

```python
annotations.LeaderLine(
    parent=self,
    start=(150, 150),      # Arrow tip (points to the target)
    elbow=(200, 100),      # Optional bend point
    end=(250, 100),        # End point (where label would go)
    stroke=colors.DARK_GRAY,
    stroke_width=1,
    arrow_size=8,          # Size of the arrowhead
)

# Straight leader line (no elbow)
annotations.LeaderLine(
    parent=self,
    start=(150, 150),
    end=(250, 100),
    stroke=colors.BLACK,
)
```

### Callout

A speech bubble / callout box with a pointer extending to a target point.

```python
annotations.Callout(
    parent=self,
    target=(200, 200),     # Point the callout points to
    box_center=(350, 100), # Center of the callout box
    box_width=100,
    box_height=50,
    pointer_width=15,      # Width of the pointer base
    corner_radius=5,       # Rounded corner radius
    fill=colors.LIGHT_YELLOW,
    stroke=colors.GOLD,
    stroke_width=1,
)
```

The pointer automatically extends from the nearest edge of the box toward the
target point.

---

## Common Properties

All extended shapes share these properties:

### Bounding Box and Anchor Points

```python
shape = polygon.Hexagon(parent=self, center=(200, 200), radius=50)

# Bounding box
bbox = shape.bbox
print(bbox.ll, bbox.ur)
print(bbox.width, bbox.height)

# Anchor points
print(shape.points.ll)
print(shape.points.ur)
print(shape.points.center)
print(shape.points.left(0.5))  # Midpoint of left edge
```

### Styling

All shapes accept:

- `fill` - Fill color (Color object, hex string, or None)
- `stroke` - Stroke color
- `stroke_width` - Stroke width (default: 1)

```python
# Using Color objects
polygon.Triangle(
    parent=self,
    center=(100, 100),
    radius=50,
    fill=colors.RED.alpha(0.5),  # Semi-transparent
    stroke=colors.DARK_RED,
    stroke_width=2,
)

# Using hex strings
polygon.Triangle(
    parent=self,
    center=(100, 100),
    radius=50,
    fill="#ff6b6b",
    stroke="#8b0000",
)
```

---

## Complete Example

```python
from od_do.diagram import Diagram
from od_do.shapes import curves, polygon, annotations, flowchart
from od_do.shapes.ellipse import Ellipse
from od_do import shapes, colors


class TechnicalDiagram(Diagram):
    def draw(self):
        # Database cylinder
        db = flowchart.Cylinder(
            parent=self,
            center=(100, 100),
            width=60,
            height=80,
            fill=colors.LIGHT_GRAY,
            stroke=colors.DARK_GRAY,
        )

        # Arrow connecting to processing box
        curves.QuadraticBezier(
            parent=self,
            start=db.points.right(0.5),
            control=(180, 60),
            end=(220, 100),
            stroke=colors.DARK_GRAY,
            stroke_width=2,
        )

        # Processing diamond
        process = flowchart.Diamond(
            parent=self,
            center=(280, 100),
            width=80,
            height=60,
            fill=colors.LIGHT_YELLOW,
            stroke=colors.GOLD,
        )

        # Output cloud
        flowchart.Cloud(
            parent=self,
            center=(420, 100),
            width=100,
            height=70,
            fill=colors.MD_CYAN,
            stroke=colors.TEAL,
        )

        # Dimension line showing width
        annotations.DimensionLine(
            parent=self,
            start=(70, 160),
            end=(130, 160),
            offset=15,
            stroke=colors.BLACK,
        )

        # Callout annotation
        annotations.Callout(
            parent=self,
            target=(100, 60),
            box_center=(100, 20),
            box_width=60,
            box_height=25,
            fill=colors.WHITE,
            stroke=colors.BLACK,
        )


diagram = TechnicalDiagram()
diagram.render("technical_diagram.svg", padding=30)
```
