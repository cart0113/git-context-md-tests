---
description:
  Two-layer architecture (shapes → diagram → backends), module layout, Diagram
  init sequence, shape registration, render pipeline, and coordinate systems
---

# Architecture

## Two-layer design

```
Shapes (primitives with position, size, styling)
    ↓ registered via parent.add_shape()
Diagram (container, bounding box, nesting)
    ↓ delegates to
Backend (SVG, PNG, Draw.io)
```

- **Shapes** (`src/od_do/shapes/`): low-level primitives.
- **Diagram** (`src/od_do/diagram/base.py`): container managing shapes, paths,
  and nested sub-diagrams.
- **Backends** (`src/od_do/diagram/backends/`): pluggable renderers.

## Module layout

```
src/od_do/
├── __init__.py         # exports cli, diagram, shapes, paths, colors, Point, BBox
├── cli.py              # Click-based CLI (141 lines)
├── config.py           # ~/.od-do-config management
├── colors.py           # Color class with .lighten(), .darken(), .alpha(), .blend()
├── geometry.py         # Point, BBox, Points, resolve_position()
├── paths.py            # Line class with direction strings (526 lines)
├── markers.py          # Arrow, Circle, Square, Diamond, Bar endpoint markers
├── placement.py        # Placement transforms for nested diagrams
├── transform.py        # Rotation/mirror transforms (R0, R90, MX, MY, MX_MY)
├── shapes/             # Shape primitives (base, curves, polygon, flowchart, etc.)
├── diagram/
│   ├── base.py         # Diagram class (398 lines)
│   └── backends/       # SVG (1684 lines), PNG (52), Draw.io (74)
└── drawio/             # Draw.io XML generation (adapted from drawpyo)
```

## Diagram init sequence — `src/od_do/diagram/base.py:82`

```
1. Diagram.__init__() called
   ├── 2. Set instance attributes (parent, width, height, units)
   ├── 3. Resolve units: param > class attr > parent > "px" (line 121)
   ├── 4. Initialize shapes list (line 143)
   ├── 5. Call self.draw() (line 147) ← subclass defines shapes here
   │       └── Shapes call parent.add_shape(self) in their __init__
   └── 6. Register with parent if parent is set (line 150)
           └── Creates Placement via placement.place() and adds to parent
```

`draw()` runs during `__init__` so all shapes exist before the diagram registers
with its parent — bounding box calculations need the full shape list.

**Custom constructor params must be set BEFORE `super().__init__()`** because
super calls `draw()`. Standard pattern:

```python
class MyComp(Diagram):
    def __init__(self, color, **kwargs):
        self.color = color          # set param first
        super().__init__(**kwargs)   # calls draw()
```

## Shape registration

Shapes auto-register: `parent.add_shape(self)` in `Shape.__init__`
(`shapes/base.py:58`).

Sub-diagrams with `parent=` create a `Placement` and register via
`parent.add_placement()` (`diagram/base.py:162`).

## Render pipeline — `Diagram.render()` at line 303

1. Resolve render options: explicit param > `render_` class attr > default.
2. Select backend from file extension or explicit `backend=` param (line 346).
3. Calculate dimensions: auto-size from bounding box if `width/height="auto"`.
4. Call `backend.render(shapes, output_path, **kwargs)`.
5. Optionally open in system viewer (`--show` flag).

## Coordinate system

SVG uses top-down Y (0 at top). Users work in bottom-up Y (0 at bottom, natural
math coordinates). The `unit_to_pixels` conversion and `resolve_position()`
handle the mapping. Shapes store `(x, y)` as upper-left internally regardless of
which corner the user specified.
