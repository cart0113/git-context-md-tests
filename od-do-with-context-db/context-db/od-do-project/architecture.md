---
description:
  High-level architecture — shapes → diagram → backends, coordinate system
  gotchas, and the init sequence trap
---

# Architecture

Shapes register themselves with a parent Diagram. Diagram delegates rendering to
a pluggable Backend (SVG, PNG, Draw.io). That's the whole architecture.

## The init sequence trap

`Diagram.__init__()` calls `self.draw()` at line 147. This means:

**Custom constructor params must be set BEFORE `super().__init__()`.** If you
set them after, `draw()` runs first and your params don't exist yet.

```python
class MyComp(Diagram):
    def __init__(self, color, **kwargs):
        self.color = color          # BEFORE super
        super().__init__(**kwargs)   # calls draw()
```

This is the single most common mistake when creating new Diagram subclasses.

## Coordinate system

SVG uses top-down Y (0 at top). Users work in bottom-up Y. Shapes store `(x, y)`
as upper-left internally regardless of which corner the user specified.
`resolve_position()` in `geometry.py` handles the conversion.

## SVG stroke/fill separation

When shapes have semi-transparent fill AND stroke, SVG strokes overlap the fill
(centered on the boundary). The SVG backend draws fill and stroke as separate
elements — fill inset by `stroke_width`, stroke with `fill="none"`. If you add a
new shape and it looks wrong with transparency, this is why.
