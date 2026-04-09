---
description:
  Backend implementations — SVG (1684-line text renderer), PNG (Pillow wrapper),
  Draw.io (XML generation adapted from drawpyo)
---

# Backends

All backends live in `src/od_do/diagram/backends/` and implement the `Backend`
ABC (`base.py`): `render(shapes, output_path, **kwargs)`.

## SVG — `svg.py` (1684 lines)

The primary backend. Generates SVG XML as text. Key internals:

- `_shape_to_svg()` — isinstance dispatch to per-shape renderers.
- Ruler/grid overlays via `--show-ruler` and `--show-grid` CLI flags.
- Text rendering with font metrics estimation.
- Handles unit-to-pixel conversion and padding offsets.

## PNG — `png.py` (52 lines)

Thin wrapper: renders to SVG first, then converts via Pillow.

## Draw.io — `drawio.py` (74 lines)

Generates Draw.io XML format. The `src/od_do/drawio/` package is adapted from
[drawpyo](https://github.com/MerrimanInd/drawpyo) (MIT License, Merrimanind,
v0.2.2).

### What was copied from drawpyo

| drawpyo source            | od-do target         | Content                     |
| ------------------------- | -------------------- | --------------------------- |
| `xml_base.py`             | `drawio/xml_base.py` | XMLBase class, XML escaping |
| `file.py`                 | `drawio/file.py`     | File class, page management |
| `page.py`                 | `drawio/page.py`     | Page, MxGraph, Root classes |
| `diagram/base_diagram.py` | `drawio/geometry.py` | Geometry class              |
| `diagram/objects.py`      | `drawio/object.py`   | Object class (simplified)   |

Not copied: edges/connectors, groups, containers, shape libraries, templates.
od-do uses its own shape system.

Modifications: added type hints, simplified initialization, renamed `xml_ify()`
to `_xml_escape()`, modern Python 3.10+ syntax.

### Draw.io XML structure

```xml
<mxfile host="od-do">
  <diagram>
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Objects here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Backend selection — `src/od_do/diagram/base.py:346`

Auto-detected from file extension, or explicit via `backend=` parameter or
`render_backend` class attribute. Falls back to SVG.
