---
description:
  Path/Line primitives, direction string parsing, StrokeLine rendering
  algorithm, arrow markers, and line style dash patterns
---

# Paths and Lines

## Core class — `src/od_do/paths.py`

`Line` (the main path class) supports absolute coordinates and direction strings
for relative movement.

### Direction strings

Parsed via regex in `paths.py`. Format: `"U20"`, `"D20"`, `"L20"`, `"R20"`.
Combine with colon for diagonal: `"D10:R10"`.

- `U` — up (decreasing Y in SVG coords).
- `D` — down (increasing Y).
- `L` — left (decreasing X).
- `R` — right (increasing X).

### Bounding box

`Path.bbox` includes marker extents calculated from marker size, line direction
at the endpoint, and perpendicular spread for the arrow base.

`BezierPath._parse_bbox()` extracts all numbers from the path string and pairs
as (x, y) to estimate bounding box. Approximate but sufficient for layout.

## StrokeLine rendering

StrokeLine renders a line with distinct edge strokes and center fill. Uses three
separate polylines to prevent semi-transparent color mixing:

1. Left edge stroke — offset perpendicular to path.
2. Right edge stroke — offset perpendicular to path.
3. Center fill — on original path at reduced width.

Edge offset: `inner_width / 2 + stroke_width / 2` where
`inner_width = width - 2 * stroke_width`.

Polyline offset at corners uses miter join calculation: compute perpendiculars
for adjacent segments, find bisector, scale by `offset / dot(perp, bisector)`.

Earlier mask-based approaches failed due to transform coordinate issues and
corner color bleeding.

## Arrow markers — `src/od_do/markers.py`

Endpoint decorations: `Arrow`, `Circle`, `Square`, `Diamond`, `Bar`.

Named sizes: `"very-small"`, `"small"`, `"medium"`, `"large"`, `"very-large"`.

When `invert=True`, arrow renders as trapezoid instead of triangle. Flat edge
matches line width: `flat_half = line_width / 2`.

## Line style dash patterns

| Style          | Dash pattern       |
| -------------- | ------------------ |
| `solid`        | None               |
| `dashed`       | (8, 4)             |
| `dotted`       | (2, 4)             |
| `dash_dot`     | (8, 4, 2, 4)       |
| `dash_dot_dot` | (8, 4, 2, 4, 2, 4) |
| `long_dash`    | (16, 6)            |
| `short_dash`   | (4, 4)             |
