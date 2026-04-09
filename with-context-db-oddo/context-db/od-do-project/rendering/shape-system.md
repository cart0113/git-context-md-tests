---
description:
  Shape base class, required properties, SVG rendering dispatch, and shape
  categories (curves, polygons, flowchart, annotations)
---

# Shape System

## Base class — `src/od_do/shapes/base.py`

`Shape` (line 25) is the base for all primitives. Required properties for
rendering compatibility:

- `x`, `y` — upper-left of bounding box (resolved from any corner in `__init__`
  at line 54 via `resolve_position()`).
- `width`, `height` — bounding box dimensions.
- `bbox` — `BBox(ll=Point, ur=Point)` (line 61).
- `points` — `Points(self)` anchor helper (line 69).
- `fill_color`, `stroke_color` — resolved to SVG-compatible strings (lines 78,
  86).

Shapes auto-register with their parent: `parent.add_shape(self)` at line 58.

## Concrete shapes in `base.py`

- `Rectangle` (line 110) — optional `corners` param for rounded corners
  (`"slightly-round"`, `"round"`, `"very-round"`, or `"round:0.15"`).
- `Circle` (line 151) — positioned by `center` or any corner. Converts center to
  `ul` internally (line 179).
- `Block` (line 185) — alias for Rectangle.
- `OpenBlock` (line 191) — 3-sided rectangle, `open_side` controls which edge is
  missing. Renders via `svg_path()` (line 211).

## SVG rendering dispatch — `src/od_do/diagram/backends/svg.py`

`SVGBackend._shape_to_svg()` dispatches by isinstance chain:

```
Circle → _circle_to_svg()
Rectangle → _rectangle_to_svg()
Ellipse → _ellipse_to_svg()
CurveBase → _curve_to_svg()      # uses shape.svg_path()
RegularPolygon → _polygon_to_svg() # uses shape.svg_points()
```

Shapes need one SVG rendering method:

- **Path-based** (curves, flowchart): `svg_path() -> str` returning SVG path
  data (`M`, `L`, `Q`, `C`, `A`, `Z` commands).
- **Polygon-based** (regular polygons, stars): `svg_points() -> str` returning
  space-separated `x,y` vertex pairs.

## SVG stroke/fill separation

When shapes have semi-transparent fill AND stroke, SVG strokes overlap the fill
(centered on boundary). Solution: draw fill and stroke as separate SVG elements.
Fill is inset by `stroke_width`, stroke has `fill="none"`. Prevents alpha
compositing artifacts.

## Shape categories

| Category       | Module                  | Rendering         | Examples                           |
| -------------- | ----------------------- | ----------------- | ---------------------------------- |
| CurveBase      | `shapes/curves.py`      | `svg_path()`      | QuadraticBezier, Arc, SemiCircle   |
| RegularPolygon | `shapes/polygon.py`     | `svg_points()`    | Triangle, Hexagon, Star            |
| Flowchart      | `shapes/flowchart.py`   | mixed             | Diamond (polygon), Cylinder (path) |
| Annotations    | `shapes/annotations.py` | multiple elements | DimensionLine, Callout             |
| Text           | `shapes/text.py`        | SVG `<text>`      | Text, TextBox, Label               |
| Table          | `shapes/table.py`       | composite         | Table, EntityTable, KeyValueTable  |
