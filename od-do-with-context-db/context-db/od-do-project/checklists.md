---
description:
  Step-by-step checklists for common multi-file tasks — adding shapes, adding
  backends, adding CLI options
---

# Checklists

## Adding a new shape

1. Create class in `src/od_do/shapes/`. Must call `parent.add_shape(self)` in
   `__init__`. Must have: `x`, `y`, `width`, `height`, `bbox`, `points`,
   `bounding_box()`, `fill_color`, `stroke_color`, `fill_opacity`,
   `stroke_opacity`.
2. Implement `svg_path()` (for path-based) or `svg_points()` (for polygons).
3. Add rendering method to `SVGBackend` in `src/od_do/diagram/backends/svg.py`.
4. Add isinstance case in `SVGBackend._shape_to_svg()` dispatch chain.
5. Export from `src/od_do/shapes/__init__.py` using
   `from .module import ClassName`.

**Gotcha:** the isinstance dispatch order matters. Put specific types before
their base classes or they'll match the wrong renderer.

## Adding a new backend

1. Create backend in `src/od_do/diagram/backends/` implementing `Backend` ABC.
2. Implement `render(shapes, output_path, **kwargs)`.
3. Add to `Diagram.render()` backend selection in `src/od_do/diagram/base.py`
   (line ~346). Match by file extension.
4. Add viewer config in `src/od_do/config.py`.

## Adding a circuit element

All elements are Diagram subclasses in `diagram_libs/basic_circuit_elements/`.

1. Set custom params BEFORE `super().__init__(**kwargs)` (see architecture.md).
2. Draw at origin `(0, 0)` — Diagram placement handles positioning.
3. Use `**kwargs` passthrough for placement options (`ul`, `rotation`, etc.).
4. Expose pin positions as `Point` properties for wire connections.
