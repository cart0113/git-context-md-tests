---
description:
  Step-by-step guide to adding new shapes and backends — required properties,
  SVG methods, dispatch registration, layer separation rules
---

# Adding New Shapes and Backends

## Adding a new shape

1. Create shape class in `src/od_do/shapes/` inheriting from `Shape`
   (`shapes/base.py:25`). Required properties: `x`, `y`, `width`, `height`,
   `bbox`, `points`, `fill_color`, `stroke_color`.
2. Implement `svg_path()` (for path-based shapes) or `svg_points()` (for
   polygon-based shapes).
3. Add a rendering method to `SVGBackend` in
   `src/od_do/diagram/backends/svg.py`.
4. Add isinstance dispatch case in `SVGBackend._shape_to_svg()`.
5. Import in `src/od_do/shapes/__init__.py`.

## Adding a new backend

1. Create backend in `src/od_do/diagram/backends/` implementing the `Backend`
   ABC (`backends/base.py`).
2. Implement `render(shapes, output_path, **kwargs)`.
3. Export from `src/od_do/diagram/backends/__init__.py`.
4. Add to backend selection logic in `Diagram.render()`
   (`src/od_do/diagram/base.py:346`).
5. Add viewer config option in `src/od_do/config.py`.

## Adding configuration options

1. Add to `config.py` defaults dict.
2. Use via `get_config()["option_name"]`.

## Adding CLI options

1. Add Click option decorator to `cli()` in `src/od_do/cli.py`.
2. Process and pass through to diagram or rendering.

## Layer separation rules

- Shapes never import backends.
- Backends handle any shape type via isinstance dispatch.
- Diagram orchestrates but doesn't render directly.
- Config is loaded once and cached globally.
