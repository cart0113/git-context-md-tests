# Placement & Transform System

The OD-DO placement system allows you to compose diagrams by placing
sub-diagrams within parent diagrams with position offsets, rotation, and
mirroring transformations.

This is a core feature of OD-DO that enables modular, reusable diagram
components.

## Quick Start

The recommended way to create components is using the `draw()` method pattern:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block, circle

# Create a reusable component by subclassing Diagram
class LEDIndicator(Diagram):
    def draw(self):
        circle(parent=self, x0=0, y0=0, radius=10, fill="#00ff00", stroke="#000")
        block(parent=self, x0=-2, y0=12, width=4, height=15, fill="#888")

# Create the main diagram
class MainDiagram(Diagram):
    def draw(self):
        # Place the LED component at different positions and rotations
        LEDIndicator(parent=self, ul=(100, 100))                # Original
        LEDIndicator(parent=self, ul=(100, 200), rotation=90)   # Rotated 90°
        LEDIndicator(parent=self, ul=(100, 350), rotation=180)  # Rotated 180°
        LEDIndicator(parent=self, ul=(100, 500), mirror="MY")   # Mirrored

diagram = MainDiagram(width=800, height=600)
diagram.render("composed_diagram.svg")
```

Notice there's no `__init__` boilerplate - just override `draw()` to define your
shapes and sub-diagrams.

## Constructor Parameters

When instantiating a Diagram subclass, you can pass these parameters:

| Parameter         | Type          | Description                                   |
| ----------------- | ------------- | --------------------------------------------- |
| `parent`          | Diagram       | Parent diagram to place this component within |
| `x`               | float         | X offset position                             |
| `y`               | float         | Y offset position                             |
| `rotation`        | float         | Rotation in degrees (0-360)                   |
| `mirror`          | str           | Mirror type: `"MX"`, `"MY"`, or `"MX_MY"`     |
| `rotation_offset` | tuple         | Custom pivot point `(x, y)` for rotation      |
| `width`           | int/float/str | Explicit width or `"auto"`                    |
| `height`          | int/float/str | Explicit height or `"auto"`                   |

## Documentation Sections

- **[Transforms](transforms.md)** - Rotation (R0-R360) and mirroring (MX, MY)
- **[Placement Basics](placement-basics.md)** - Positioning diagrams with x, y
  offset
- **[Rotation Offset](rotation-offset.md)** - Advanced rotation around custom
  pivot points
- **[Combining Transforms](combining-transforms.md)** - Using rotation and
  mirror together
- **[API Reference](api-reference.md)** - Complete API documentation

---

# Placement Basics

In OD-DO, you compose diagrams by placing sub-diagrams within parent diagrams.
The `draw()` method pattern makes this clean and intuitive.

## Core Concept

The placement system allows you to:

1. **Reuse** - Create diagram components once, place them multiple times
2. **Position** - Offset content to any (x, y) coordinate
3. **Transform** - Apply rotation and/or mirroring to each instance

## The `draw()` Method Pattern

Instead of manually creating placements, define your components as `Diagram`
subclasses with a `draw()` method:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import circle

class LED(Diagram):
    def draw(self):
        circle(parent=self, x0=0, y0=0, radius=10, fill="#00ff00", stroke="#000")

class LEDRow(Diagram):
    def draw(self):
        # Place LED components at different positions
        LED(parent=self, ul=(0, 0))
        LED(parent=self, ul=(30, 0))
        LED(parent=self, ul=(60, 0))
        LED(parent=self, ul=(90, 0))

# Create and render
diagram = LEDRow()
diagram.render("led_row.svg")
```

## Understanding the Coordinate System

When you place a component:

- The component's shapes are defined relative to (0, 0)
- The placement's (x, y) moves the origin to that position
- All shapes in the component move with the origin

```
Component definition:          After placement at ul=(100, 50:
         (0),0)                       (100,50)
           ┌─────────┐                  ┌─────────┐
           │  Shape  │                  │  Shape  │
           └─────────┘                  └─────────┘

Shape at (10, 20) in component → appears at (110, 70) in parent
```

## Basic Positioning with x, y

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block

class Resistor(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=60, height=20, fill="#d4a574")

class ResistorGrid(Diagram):
    def draw(self):
        # Place resistors in a grid
        for row in range(3):
            for col in range(4):
                Resistor(parent=self, ul=(50 + col * 100, 50 + row * 100))

diagram = ResistorGrid(width=500, height=400)
diagram.render("resistor_grid.svg")
```

## Multiple Instances

A key benefit of the pattern is creating multiple instances of the same
component:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block, circle

class Chip(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=100, height=60, fill="#2c3e50")
        # Add pins
        for i in range(5):
            circle(parent=self, x0=10 + i * 20, y0=-5, radius=3, fill="#bdc3c7")
            circle(parent=self, x0=10 + i * 20, y0=62, radius=3, fill="#bdc3c7")

class PCB(Diagram):
    def draw(self):
        # Place multiple chips
        Chip(parent=self, ul=(50, 50))
        Chip(parent=self, ul=(200, 50))
        Chip(parent=self, ul=(350, 50))
        Chip(parent=self, ul=(50, 200))
        Chip(parent=self, ul=(200, 200))
        Chip(parent=self, ul=(350, 200))

diagram = PCB(width=600, height=400)
diagram.render("pcb_with_chips.svg")
```

## Combining Position with Transform

Position and transforms work together:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block

class Arrow(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=10, width=40, height=20, fill="#1abc9c")
        block(parent=self, x0=35, y0=0, width=20, height=40, fill="#1abc9c")

class DirectionalArrows(Diagram):
    def draw(self):
        # Place arrows pointing in different directions
        Arrow(parent=self, ul=(50, 50))                  # Right
        Arrow(parent=self, ul=(200, 50), rotation=90)    # Down
        Arrow(parent=self, ul=(350, 50), rotation=180)   # Left
        Arrow(parent=self, ul=(50, 200), rotation=270)   # Up

diagram = DirectionalArrows(width=500, height=400)
diagram.render("directional_arrows.svg")
```

## Nested Placements

Components can be nested to any depth:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import block

class Square(Diagram):
    def draw(self):
        block(parent=self, x0=0, y0=0, width=20, height=20, fill="#e74c3c")

class Row(Diagram):
    def draw(self):
        for i in range(3):
            Square(parent=self, ul=(i * 30, 0))

class Grid(Diagram):
    def draw(self):
        for j in range(3):
            Row(parent=self, ul=(0, j * 30))

class MainDiagram(Diagram):
    def draw(self):
        Grid(parent=self, ul=(50, 50))
        Grid(parent=self, ul=(200, 50), rotation=45)
        Grid(parent=self, ul=(400, 50), mirror="MY")

diagram = MainDiagram(width=600, height=400)
diagram.render("nested_placements.svg")
```

## Custom Component Parameters

If your component needs custom parameters, set them before calling
`super().__init__()`:

```python
from od_do.diagram.base import Diagram
from od_do.shapes.factory import circle

class LED(Diagram):
    def __init__(self, color, **kwargs):
        self.color = color  # Set BEFORE super().__init__()
        super().__init__(**kwargs)

    def draw(self):
        circle(parent=self, x0=0, y0=0, radius=10, fill=self.color, stroke="#000")

class LEDPanel(Diagram):
    def draw(self):
        LED(color="#ff0000", parent=self, ul=(0, 0))    # Red
        LED(color="#00ff00", parent=self, ul=(30, 0))   # Green
        LED(color="#0000ff", parent=self, ul=(60, 0))   # Blue
```

## Best Practices

1. **Override `draw()`, not `__init__`** - Unless you need custom constructor
   parameters

2. **Design components from origin** - Place component shapes starting near
   (0, 0) for predictable positioning

3. **Keep components small and focused** - Create atomic components that can be
   combined

4. **Use meaningful names** - Name your component classes descriptively

5. **Consider rotation center** - When designing components that will be
   rotated, think about where the pivot point should be (see
   [Rotation Offset](rotation-offset.md))

---

# Transforms

Transforms in OD-DO define rotation and mirroring operations applied to
placements. The `Transform` class encapsulates these operations.

## Rotation (R0 to R360)

Rotation is specified in degrees, from 0 to 360. The rotation is applied around
a pivot point (see [Rotation Offset](rotation-offset.md) for details on
specifying custom pivot points).

### Common Rotations

| Rotation | Description                                      |
| -------- | ------------------------------------------------ |
| R0       | No rotation (identity)                           |
| R90      | 90 degrees clockwise                             |
| R180     | 180 degrees (upside down)                        |
| R270     | 270 degrees clockwise (or 90° counter-clockwise) |

### Using Rotation

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create a simple component
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=80, height=40, fill="#3498db"))

# Create main diagram
main = Diagram(width=600, height=400)

# Place with different rotations
main.place(component, ul=(50, 50))              # R0 - no rotation
main.place(component, ul=(200, 50), rotation=45)   # R45
main.place(component, ul=(350, 50), rotation=90)   # R90
main.place(component, ul=(50, 200), rotation=135)  # R135
main.place(component, ul=(200, 200), rotation=180) # R180
main.place(component, ul=(350, 200), rotation=270) # R270

main.render("rotation_examples.svg")
```

### Any Angle

You can specify any angle from 0 to 360:

```python
main.place(component, ul=(100, 100), rotation=45)    # 45 degrees
main.place(component, ul=(200, 100), rotation=22.5)  # 22.5 degrees
main.place(component, ul=(300, 100), rotation=135)   # 135 degrees
```

## Mirroring (MX and MY)

Mirroring creates a reflection of the content across an axis.

### Mirror Types

| Mirror | Description                              |
| ------ | ---------------------------------------- |
| MX     | Mirror across X axis (flip vertically)   |
| MY     | Mirror across Y axis (flip horizontally) |
| MX_MY  | Mirror across both axes                  |

### MX - Mirror X (Flip Vertically)

Flips the content upside down by mirroring across the X axis:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create an asymmetric component to see the mirror effect
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=60, height=40, fill="#e74c3c"))
component.add_shape(block(x0=0, y0=0, width=20, height=20, fill="#f39c12"))  # Corner marker

main = Diagram(width=400, height=300)

# Original
main.place(component, ul=(50, 50))

# Mirrored across X (flipped vertically)
main.place(component, ul=(200, 50), mirror="MX")

main.render("mirror_x_example.svg")
```

### MY - Mirror Y (Flip Horizontally)

Flips the content left-to-right by mirroring across the Y axis:

```python
main = Diagram(width=400, height=300)

# Original
main.place(component, ul=(50, 50))

# Mirrored across Y (flipped horizontally)
main.place(component, ul=(200, 50), mirror="MY")

main.render("mirror_y_example.svg")
```

### MX_MY - Mirror Both Axes

Mirrors across both axes (equivalent to 180-degree rotation for symmetric
shapes):

```python
main = Diagram(width=400, height=300)

# Original
main.place(component, ul=(50, 50))

# Mirrored across both axes
main.place(component, ul=(200, 50), mirror="MX_MY")

main.render("mirror_both_example.svg")
```

## Transform Class

For more control, you can use the `Transform` class directly:

```python
from od_do.transform import Transform, Mirror, R90, R180, MX, MY

# Create transforms
rot_90 = Transform(rotation=90)
rot_180 = Transform(rotation=180)
mirror_x = Transform(mirror=Mirror.MX)
mirror_y = Transform(mirror=Mirror.MY)

# Or use convenience constants
from od_do.transform import R0, R90, R180, R270, MX, MY, MXY
```

### Parsing Transform Strings

Transform can parse string representations:

```python
from od_do.transform import Transform

t1 = Transform.from_string("R90")      # 90 degree rotation
t2 = Transform.from_string("MX")       # Mirror X
t3 = Transform.from_string("R180_MX")  # 180 rotation + Mirror X
t4 = Transform.from_string("R45_MY")   # 45 rotation + Mirror Y
```

### Transform Order

When both rotation and mirroring are applied, the order is:

1. Mirror operations are applied first
2. Rotation is applied second

This means `R90_MX` first mirrors across X, then rotates 90 degrees.

## Visual Reference

```
Original (R0):          R90:                R180:               R270:
┌────────────┐         ┌───┐               ┌────────────┐       ┌───┐
│ █          │         │   │               │          █ │       │   │
│            │         │   │               │            │       │   │
└────────────┘         │ █ │               └────────────┘       │   │
                       └───┘                                    │ █ │
                                                                └───┘

MX (flip vertical):    MY (flip horizontal):   MX_MY:
┌────────────┐         ┌────────────┐          ┌────────────┐
│            │         │          █ │          │            │
│ █          │         │            │          │          █ │
└────────────┘         └────────────┘          └────────────┘
```

The █ represents a corner marker to show orientation.

---

# Rotation Offset

The `rotation_offset` parameter provides precise control over where rotation
occurs. By default, rotation happens around the placement's origin (x, y). With
`rotation_offset`, you can specify a different pivot point.

## Understanding Rotation Pivot Points

When rotating a placed component, the rotation occurs around a pivot point. The
`rotation_offset` defines this pivot point relative to the placement position.

### Default Behavior (No rotation_offset)

By default, rotation occurs around the placement origin:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create a bar component
bar = Diagram()
bar.add_shape(block(x0=0, y0=0, width=100, height=20, fill="#3498db"))

main = Diagram(width=400, height=300)

# Place at (100, 100) with 45-degree rotation
# Rotates around point (100, 100) - the placement origin
main.place(bar, ul=(100, 100), rotation=45)

main.render("default_rotation.svg")
```

```
Pivot point (100, 100) is at the placement origin:

        ╱╲
       ╱  ╲
      ╱    ╲
     ╱      ╲
    ●────────   ← The bar rotates around its top-left corner
 (100,100)
```

### With rotation_offset

When you specify `rotation_offset=(ox, oy)`, the pivot point becomes
`(x + ox, y + oy)`:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create a bar component
bar = Diagram()
bar.add_shape(block(x0=0, y0=0, width=100, height=20, fill="#3498db"))

main = Diagram(width=400, height=300)

# Place at (100, 100) with rotation around the CENTER of the bar
# Bar is 100x20, so center is at (50, 10) relative to bar origin
main.place(bar, ul=(100, 100), rotation=45, rotation_offset=(50, 10))

main.render("centered_rotation.svg")
```

```
Pivot point is at (150, 110) which is the center of the bar:

       ╲     ╱
        ╲   ╱
         ╲●╱    ← Rotates around center point
         ╱╲
        ╱  ╲
```

## Transform Order Explained

The complete transform sequence is:

1. **Translate to (x, y)** - Move the component origin to the placement position
2. **Calculate pivot** - Pivot is at (x + rotation_offset_x, y +
   rotation_offset_y)
3. **Apply rotation around pivot** - Rotate by the specified angle around the
   pivot point

### Example: Rotating Around an Offset Point

From the original example in the task description:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

component = Diagram()
component.add_shape(block(x0=0, y0=0, width=50, height=30, fill="#e74c3c"))

main = Diagram(width=400, height=400)

# Place at (10, 20), with rotation_offset (100, 100) and 180-degree rotation
# Step 1: Shape is placed at (10, 20)
# Step 2: Pivot point is at (10 + 100, 20 + 100) = (110, 120)
# Step 3: Shape rotates 180 degrees around point (110, 120)

main.place(component, ul=(10, 20), rotation=180, rotation_offset=(100, 100))

main.render("rotation_offset_example.svg")
```

```
Visual representation:

Before rotation:
(10,20)
  ┌─────┐
  │ Bar │
  └─────┘
                    ● (110, 120) pivot point

After 180° rotation around (110, 120):
                    ● (110, 120) pivot point

                              ┌─────┐
                              │ Bar │  (appears on the other side)
                              └─────┘
```

## Common Use Cases

### 1. Rotate Around Center

For many components, you want rotation around the center:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Square component 60x60
square = Diagram()
square.add_shape(block(x0=0, y0=0, width=60, height=60, fill="#9b59b6"))

main = Diagram(width=400, height=400)

# Place and rotate around center (30, 30)
main.place(square, ul=(100, 100), rotation=45, rotation_offset=(30, 30))

main.render("center_rotation.svg")
```

### 2. Rotate Around a Connection Point

When creating connected diagrams, you might want to rotate around a connection
point:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block, circle

# An arm with a pivot at one end
arm = Diagram()
arm.add_shape(block(x0=0, y0=-5, width=80, height=10, fill="#2ecc71"))
arm.add_shape(circle(x0=-5, y0=-5, radius=5, fill="#27ae60"))  # Pivot joint

main = Diagram(width=400, height=400)

# Place multiple arms rotating around their pivot joint
for angle in [0, 30, 60, 90, 120, 150]:
    main.place(arm, ul=(200, 200), rotation=angle, rotation_offset=(0, 0))

main.render("rotating_arms.svg")
```

### 3. Create Patterns with Offset Rotation

Create radial patterns by rotating around an external point:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# A small element
element = Diagram()
element.add_shape(block(x0=0, y0=0, width=30, height=10, fill="#f1c40f"))

main = Diagram(width=400, height=400)

# Create a circular pattern
# Element is placed 80 pixels from center (200, 200)
# Then rotated around the center
for i in range(12):
    angle = i * 30  # 0, 30, 60, ... 330
    main.place(
        element,
        x=200 - 15,  # Offset so element centers at (200, y)
        y=200 - 80,  # Place 80px above center
        rotation=angle,
        rotation_offset=(15, 80)  # Rotate around the diagram center
    )

main.render("radial_pattern.svg")
```

### 4. Mechanical Linkages

Simulate mechanical systems with rotation around joints:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block, circle

# Link with pivot holes at each end
link = Diagram()
link.add_shape(block(x0=0, y0=-5, width=100, height=10, fill="#95a5a6"))
link.add_shape(circle(x0=-2, y0=-2, radius=4, fill="none", stroke="#000"))
link.add_shape(circle(x0=96, y0=-2, radius=4, fill="none", stroke="#000"))

main = Diagram(width=500, height=400)

# Fixed pivot at left
main.place(link, ul=(100, 200), rotation=0, rotation_offset=(0, 0))

# Another link attached at first link's right end, rotated 30°
main.place(link, ul=(200, 200), rotation=30, rotation_offset=(0, 0))

main.render("linkage.svg")
```

## Combining rotation_offset with Mirror

When using both `rotation_offset` and `mirror`, the mirror is applied first,
then rotation:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Asymmetric component
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=60, height=40, fill="#e74c3c"))
component.add_shape(block(x0=0, y0=0, width=15, height=15, fill="#f39c12"))

main = Diagram(width=600, height=400)

# Original
main.place(component, ul=(50, 50))

# Mirrored and rotated 90 around center
main.place(
    component,
    ul=(200, 50),
    rotation=90,
    mirror="MY",
    rotation_offset=(30, 20)  # Center of the component
)

main.render("mirror_and_rotate.svg")
```

## Tips for Using rotation_offset

1. **Calculate center for symmetric rotation**
   - For a shape at (0, 0) with width W and height H
   - Center is at `rotation_offset=(W/2, H/2)`

2. **Use (0, 0) for corner rotation**
   - Default behavior, no offset needed
   - Useful when connecting components at corners

3. **Visualize the pivot point**
   - Add a small marker at the pivot during development
   - Remove it once positioning is correct

4. **Test with extreme angles**
   - 0°, 90°, 180°, 270° are good tests
   - These reveal offset calculation errors quickly

---

# Combining Transforms

OD-DO supports combining rotation and mirroring in a single placement. This page
explains how these transformations interact and the order in which they're
applied.

## Transform Application Order

When both rotation and mirroring are specified, they are applied in this order:

1. **Mirror first** - The content is mirrored (MX, MY, or both)
2. **Rotation second** - The mirrored content is then rotated

This order matters because `R90 + MX` produces different results than
`MX + R90`.

## Using Rotation with Mirror

### Rotation + MX (Mirror X)

MX flips vertically, then rotation is applied:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# L-shaped component
el = Diagram()
el.add_shape(block(x0=0, y0=0, width=60, height=20, fill="#3498db"))
el.add_shape(block(x0=0, y0=0, width=20, height=60, fill="#3498db"))

main = Diagram(width=600, height=400)

# Original
main.place(el, ul=(50, 50))

# MX only (flipped vertically)
main.place(el, ul=(150, 50), mirror="MX")

# R90 only
main.place(el, ul=(250, 50), rotation=90)

# R90 + MX (mirror first, then rotate)
main.place(el, ul=(350, 50), rotation=90, mirror="MX")

main.render("rotation_with_mx.svg")
```

```
Original:    MX:          R90:         R90+MX:
┌───────     ─────────┐   ─┐           ┌─
│            │            │           │
│            ─────────┘   │           │
└───────                  │           │
                          │           │
                          └───────    ───────┘
```

### Rotation + MY (Mirror Y)

MY flips horizontally, then rotation is applied:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# L-shaped component
el = Diagram()
el.add_shape(block(x0=0, y0=0, width=60, height=20, fill="#e74c3c"))
el.add_shape(block(x0=0, y0=0, width=20, height=60, fill="#e74c3c"))

main = Diagram(width=600, height=400)

# Original
main.place(el, ul=(50, 50))

# MY only (flipped horizontally)
main.place(el, ul=(150, 50), mirror="MY")

# R90 only
main.place(el, ul=(250, 50), rotation=90)

# R90 + MY (mirror first, then rotate)
main.place(el, ul=(350, 50), rotation=90, mirror="MY")

main.render("rotation_with_my.svg")
```

### Rotation + MX_MY (Both Mirrors)

MX_MY (or "MX_MY") mirrors across both axes, then rotation is applied:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Arrow-like component
arrow = Diagram()
arrow.add_shape(block(x0=0, y0=10, width=50, height=20, fill="#9b59b6"))
arrow.add_shape(block(x0=40, y0=0, width=20, height=40, fill="#9b59b6"))

main = Diagram(width=700, height=300)

# Original
main.place(arrow, ul=(50, 100))

# MX_MY (equivalent to 180° for this symmetric shape)
main.place(arrow, ul=(150, 100), mirror="MX_MY")

# R45
main.place(arrow, ul=(300, 100), rotation=45)

# R45 + MX_MY
main.place(arrow, ul=(500, 100), rotation=45, mirror="MX_MY")

main.render("rotation_with_mxy.svg")
```

## Common Combined Transformations

### Eight Orientations

For many applications, you need all 8 possible orientations (4 rotations × 2
mirror states):

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Asymmetric component
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=50, height=30, fill="#1abc9c"))
component.add_shape(block(x0=0, y0=0, width=15, height=15, fill="#16a085"))

main = Diagram(width=800, height=400)

# Row 1: No mirror, 4 rotations
main.place(component, ul=(50, 50), rotation=0)
main.place(component, ul=(150, 50), rotation=90)
main.place(component, ul=(250, 50), rotation=180)
main.place(component, ul=(350, 50), rotation=270)

# Row 2: MY mirror, 4 rotations
main.place(component, ul=(50, 150), rotation=0, mirror="MY")
main.place(component, ul=(150, 150), rotation=90, mirror="MY")
main.place(component, ul=(250, 150), rotation=180, mirror="MY")
main.place(component, ul=(350, 150), rotation=270, mirror="MY")

main.render("eight_orientations.svg")
```

### PCB/IC Orientations

Electronics often use standard orientation codes:

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# IC package (asymmetric with pin 1 indicator)
ic = Diagram()
ic.add_shape(block(x0=0, y0=0, width=80, height=40, fill="#2c3e50"))
ic.add_shape(block(x0=5, y0=5, width=10, height=10, fill="#ecf0f1"))  # Pin 1 dot

main = Diagram(width=600, height=500)

# Standard PCB orientations
placements = [
    {"x": 50,  "y": 50,  "rotation": 0,   "mirror": None,  "label": "R0"},
    {"x": 200, "y": 50,  "rotation": 90,  "mirror": None,  "label": "R90"},
    {"x": 350, "y": 50,  "rotation": 180, "mirror": None,  "label": "R180"},
    {"x": 500, "y": 50,  "rotation": 270, "mirror": None,  "label": "R270"},
    {"x": 50,  "y": 150, "rotation": 0,   "mirror": "MY",  "label": "R0_MY"},
    {"x": 200, "y": 150, "rotation": 90,  "mirror": "MY",  "label": "R90_MY"},
    {"x": 350, "y": 150, "rotation": 180, "mirror": "MY",  "label": "R180_MY"},
    {"x": 500, "y": 150, "rotation": 270, "mirror": "MY",  "label": "R270_MY"},
]

for p in placements:
    main.place(ic, ul=(p["x"], p["y"]), rotation=p["rotation"], mirror=p["mirror"])

main.render("ic_orientations.svg")
```

## Transform Equivalences

Some transform combinations produce equivalent results:

| Transforms     | Equivalent To |
| -------------- | ------------- |
| R180 + MX + MY | R0 (identity) |
| R180           | MX + MY       |
| R90 + R90      | R180          |
| MX + MX        | R0 (identity) |
| MY + MY        | R0 (identity) |

```python
from od_do.transform import Transform, Mirror

# These produce the same result:
t1 = Transform(rotation=180)
t2 = Transform(mirror=Mirror.MXY)

# These are equivalent for symmetric shapes:
t3 = Transform(rotation=90, mirror=Mirror.MX)
t4 = Transform(rotation=270, mirror=Mirror.MY)
```

## Using Transform Objects Directly

For complex scenarios, create Transform objects:

```python
from od_do.transform import Transform, Mirror
from od_do.placement import Placement
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create component
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=40, height=25, fill="#f39c12"))

# Create transform
my_transform = Transform(rotation=45, mirror=Mirror.MY)

# Create placement with transform
placement = Placement(
    source=component,
    ul=(100, 100),
    transform=my_transform,
    rotation_offset_x=20,
    rotation_offset_y=12.5,  # Center of component
)

main = Diagram(width=300, height=300)
main.add_placement(placement)
main.render("transform_object.svg")
```

## Combining with rotation_offset

When combining rotation, mirror, and rotation_offset:

1. Content is translated to (x, y)
2. Mirror is applied around the pivot point (x + rotation_offset_x, y +
   rotation_offset_y)
3. Rotation is applied around the same pivot point

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Asymmetric component 60x40
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=60, height=40, fill="#e74c3c"))
component.add_shape(block(x0=0, y0=0, width=20, height=15, fill="#c0392b"))

main = Diagram(width=600, height=400)

# Original at center
main.place(component, ul=(100, 100))

# All transforms around center (30, 20)
center_offset = (30, 20)

main.place(component, ul=(250, 100), rotation=45, rotation_offset=center_offset)
main.place(component, ul=(400, 100), rotation=45, mirror="MY", rotation_offset=center_offset)

main.render("combined_transforms.svg")
```

## Best Practices

1. **Be consistent** - Choose a mirror convention and stick to it
2. **Test visually** - Generate SVGs to verify transform results
3. **Use center offsets** - For most symmetric rotations, offset to the center
4. **Document orientations** - Comment which orientation each placement uses
5. **Create helper functions** - For repeated patterns, wrap common transform
   combinations

---

# API Reference

Complete API documentation for the OD-DO placement and transform system.

## Transform Module

### Class: Transform

```python
from od_do.transform import Transform
```

Represents a transformation consisting of rotation and/or mirroring.

#### Constructor

```python
Transform(rotation: float = 0, mirror: Mirror = Mirror.NONE)
```

| Parameter  | Type   | Default     | Description                     |
| ---------- | ------ | ----------- | ------------------------------- |
| `rotation` | float  | 0           | Rotation in degrees (0-360)     |
| `mirror`   | Mirror | Mirror.NONE | Mirror type (NONE, MX, MY, MXY) |

#### Class Methods

##### `from_string(transform_str: str) -> Transform`

Parse a transform string like "R90", "MX", "R180_MX".

```python
t = Transform.from_string("R90_MX")  # 90° rotation + mirror X
```

**Format:**

- `R{degrees}` for rotation (e.g., R90, R180, R45)
- `MX` for mirror X (flip vertically)
- `MY` for mirror Y (flip horizontally)
- Combine with underscore: `R90_MX`, `R180_MY`, `MX_MY`

#### Instance Methods

##### `to_string() -> str`

Convert transform to string representation.

```python
t = Transform(rotation=90, mirror=Mirror.MX)
print(t.to_string())  # "R90_MX"
```

##### `to_svg_transform(center_x: float, center_y: float) -> str`

Generate SVG transform attribute value.

```python
t = Transform(rotation=45)
svg_attr = t.to_svg_transform(100, 100)
# Returns: "rotate(45 100 100)"
```

##### `is_identity() -> bool`

Check if this transform is the identity (no-op).

```python
t1 = Transform()
print(t1.is_identity())  # True

t2 = Transform(rotation=90)
print(t2.is_identity())  # False
```

#### Properties

| Property   | Type   | Description                       |
| ---------- | ------ | --------------------------------- |
| `rotation` | float  | Rotation angle in degrees (0-360) |
| `mirror`   | Mirror | Mirror type enum value            |

---

### Enum: Mirror

```python
from od_do.transform import Mirror
```

Mirror transformation types.

| Value         | Description                              |
| ------------- | ---------------------------------------- |
| `Mirror.NONE` | No mirroring                             |
| `Mirror.MX`   | Mirror across X axis (flip vertically)   |
| `Mirror.MY`   | Mirror across Y axis (flip horizontally) |
| `Mirror.MXY`  | Mirror across both axes                  |

---

### Convenience Constants

```python
from od_do.transform import R0, R90, R180, R270, MX, MY, MXY
```

| Constant | Equivalent To                  |
| -------- | ------------------------------ |
| `R0`     | `Transform(rotation=0)`        |
| `R90`    | `Transform(rotation=90)`       |
| `R180`   | `Transform(rotation=180)`      |
| `R270`   | `Transform(rotation=270)`      |
| `MX`     | `Transform(mirror=Mirror.MX)`  |
| `MY`     | `Transform(mirror=Mirror.MY)`  |
| `MXY`    | `Transform(mirror=Mirror.MXY)` |

---

## Placement Module

### Class: Placement

```python
from od_do.placement import Placement
```

Represents the placement of a diagram or shape group within another diagram.

#### Constructor

```python
Placement(
    source: Union[Diagram, List[Shape]],
    x: float = 0,
    y: float = 0,
    transform: Optional[Transform] = None,
    rotation_offset_x: Optional[float] = None,
    rotation_offset_y: Optional[float] = None,
)
```

| Parameter           | Type                   | Default  | Description                 |
| ------------------- | ---------------------- | -------- | --------------------------- |
| `source`            | Diagram \| List[Shape] | required | The content to place        |
| `x`                 | float                  | 0        | X offset position           |
| `y`                 | float                  | 0        | Y offset position           |
| `transform`         | Transform \| None      | None     | Transform to apply          |
| `rotation_offset_x` | float \| None          | None     | X offset for rotation pivot |
| `rotation_offset_y` | float \| None          | None     | Y offset for rotation pivot |

#### Class Methods

##### `create(...) -> Placement`

Convenience factory method with simplified parameters.

```python
placement = Placement.create(
    source=my_diagram,
    ul=(100, 100),
    rotation=45,
    mirror="MX",
    rotation_offset=(50, 25),
)
```

| Parameter         | Type                   | Default  | Description                            |
| ----------------- | ---------------------- | -------- | -------------------------------------- |
| `source`          | Diagram \| List[Shape] | required | The content to place                   |
| `x`               | float                  | 0        | X offset position                      |
| `y`               | float                  | 0        | Y offset position                      |
| `rotation`        | float                  | 0        | Rotation in degrees                    |
| `mirror`          | str \| None            | None     | Mirror type: "MX", "MY", or "MX_MY"    |
| `rotation_offset` | tuple \| None          | None     | (x, y) tuple for rotation pivot offset |

#### Instance Methods

##### `get_shapes() -> List[Shape]`

Get the shapes from the source.

```python
shapes = placement.get_shapes()
```

##### `get_rotation_pivot() -> tuple`

Calculate the rotation pivot point (x, y).

```python
pivot_x, pivot_y = placement.get_rotation_pivot()
```

##### `to_svg_group() -> str`

Generate SVG `<g>` element with transforms.

```python
svg = placement.to_svg_group()
```

#### Properties

| Property            | Type                   | Description                        |
| ------------------- | ---------------------- | ---------------------------------- |
| `source`            | Diagram \| List[Shape] | The source content                 |
| `x`                 | float                  | X offset position                  |
| `y`                 | float                  | Y offset position                  |
| `transform`         | Transform              | Transform to apply                 |
| `rotation_offset_x` | float \| None          | X offset for rotation pivot        |
| `rotation_offset_y` | float \| None          | Y offset for rotation pivot        |
| `has_transform`     | bool                   | True if any non-identity transform |

---

### Function: place

```python
from od_do.placement import place
```

Convenience function to create a Placement.

```python
place(
    source: Union[Diagram, List[Shape]],
    x: float = 0,
    y: float = 0,
    rotation: float = 0,
    mirror: Optional[str] = None,
    rotation_offset: Optional[tuple] = None,
) -> Placement
```

**Example:**

```python
from od_do.placement import place

# Simple placement
p1 = place(my_diagram, ul=(100, 200))

# With rotation
p2 = place(my_diagram, ul=(100, 200), rotation=90)

# With rotation offset
p3 = place(my_diagram, ul=(10, 20), rotation=180, rotation_offset=(100, 100))

# With mirror
p4 = place(my_diagram, ul=(50, 50), mirror="MY")
```

---

## Diagram Class Extensions

### Method: place

```python
diagram.place(
    source: Union[Diagram, List[Shape]],
    x: float = 0,
    y: float = 0,
    rotation: float = 0,
    mirror: Optional[str] = None,
    rotation_offset: Optional[tuple] = None,
) -> Placement
```

Place a sub-diagram or shapes with position and transformation.

**Returns:** The created Placement instance

**Example:**

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block

# Create component
component = Diagram()
component.add_shape(block(x0=0, y0=0, width=50, height=30, fill="#3498db"))

# Create main diagram and place component
main = Diagram(width=400, height=300)
main.place(component, ul=(100, 100), rotation=45)
main.render("output.svg")
```

---

### Method: add_placement

```python
diagram.add_placement(placement: Placement)
```

Add a placement (sub-diagram with transforms) to this diagram.

**Example:**

```python
from od_do.placement import Placement
from od_do.transform import Transform

p = Placement(
    source=component,
    ul=(100, 100),
    transform=Transform(rotation=45),
)
main.add_placement(p)
```

---

## SVG Output

The SVG backend renders placements as `<g>` (group) elements with transform
attributes:

```xml
<g transform="translate(100, 100) rotate(45 50 25)">
  <rect x="0" y="0" width="100" height="50" fill="#3498db"/>
</g>
```

### Transform Attribute Format

| Transform   | SVG Output                                            |
| ----------- | ----------------------------------------------------- |
| Translation | `translate(x, y)`                                     |
| Rotation    | `rotate(angle centerX centerY)`                       |
| Mirror X    | `translate(cx, cy) scale(1, -1) translate(-cx, -cy)`  |
| Mirror Y    | `translate(cx, cy) scale(-1, 1) translate(-cx, -cy)`  |
| Mirror XY   | `translate(cx, cy) scale(-1, -1) translate(-cx, -cy)` |

Multiple transforms are concatenated with spaces:

```xml
<g transform="translate(100, 100) translate(50, 25) scale(-1, 1) translate(-50, -25) rotate(45 50 25)">
```

---

## Complete Example

```python
from od_do.diagram.base import Diagram
from od_do.shapes import block, circle
from od_do.placement import place, Placement
from od_do.transform import Transform, Mirror

# Create a reusable component
led_indicator = Diagram()
led_indicator.add_shape(circle(x0=0, y0=0, radius=8, fill="#00ff00", stroke="#000"))
led_indicator.add_shape(block(x0=-2, y0=10, width=4, height=15, fill="#888"))
led_indicator.add_shape(block(x0=-2, y0=25, width=4, height=15, fill="#888"))

# Create main PCB diagram
pcb = Diagram(width=400, height=300)

# Add LEDs using various methods

# Method 1: Diagram.place() - simplest
pcb.place(led_indicator, ul=(50, 50))

# Method 2: place() function
led_rotated = place(led_indicator, ul=(100, 50), rotation=90)
pcb.add_placement(led_rotated)

# Method 3: Placement.create()
led_mirrored = Placement.create(
    source=led_indicator,
    ul=(150, 50),
    rotation=180,
    mirror="MY",
)
pcb.add_placement(led_mirrored)

# Method 4: Placement constructor with Transform
led_complex = Placement(
    source=led_indicator,
    ul=(200, 50),
    transform=Transform(rotation=45, mirror=Mirror.MX),
    rotation_offset_x=0,
    rotation_offset_y=20,  # Rotate around LED center
)
pcb.add_placement(led_complex)

# Render
pcb.render("pcb_leds.svg")
```
