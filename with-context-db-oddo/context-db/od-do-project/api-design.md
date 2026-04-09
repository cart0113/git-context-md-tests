---
description:
  API design principles — Point interop, positioning, anchor points, direction
  strings, colors
---

# API Design Principles

## Point Interoperability

Anywhere a `Point` is accepted as input, a 2-tuple of numbers `(x, y)` is also
accepted. This applies to shape positioning parameters, path start points, and
any function that takes coordinate inputs.

## Shape and Diagram Positioning

Both shapes and diagrams use corner-based positioning:

- `ll` (lower-left) — default if none specified, defaults to `(0, 0)`
- `ul` (upper-left)
- `lr` (lower-right)
- `ur` (upper-right)
- `center` (circles only)

Error if more than one position is specified.

## Anchor Points

All shapes have:

- `.bbox` property returning `BBox(ll=Point, ur=Point)`
- `.points` property providing access to:
  - Corner points: `.points.ll`, `.points.ul`, `.points.lr`, `.points.ur`,
    `.points.center`
  - Edge interpolation: `.points.left(t)`, `.points.right(t)`, `.points.top(t)`,
    `.points.bottom(t)` (t: 0.0-1.0)

## Direction Strings for Paths

Paths support direction strings for relative movement:

- `"U20"` — Up 20 units (decreasing Y in SVG coords)
- `"D20"` — Down 20 units (increasing Y)
- `"L20"` — Left 20 units (decreasing X)
- `"R20"` — Right 20 units (increasing X)

Combine with colon: `"D10:R10"` for diagonal movement.

## Color Manipulation

The `colors` module provides:

- Predefined constants: `colors.RED`, `colors.DARK_BLUE`, etc.
- Manipulation methods: `.lighten(0.3)`, `.darken(0.2)`, `.alpha(0.5)`,
  `.blend(other, 0.5)`
