---
description:
  Non-obvious traps, past bugs, and debugging patterns — things that will bite
  you if you don't know about them
---

# Gotchas

## Never put exit() in module-level code paths

`transform.py` defines module-level constants like `R0 = Transform(rotation=0)`.
A stray `exit()` in `Transform.__init__()` fired during import, silently killing
Python with no traceback. No error message, no crash — just stops.

Symptom: anything that triggers `from od_do.placement import ...` dies silently.
Standalone diagrams (no parent) work fine because the import is deferred until a
child diagram registers with a parent (`Diagram.__init__` line ~151).

**Rule:** never put `exit()`, `sys.exit()`, or `quit()` in constructors,
especially classes with module-level instances.

## PascalCase for shape constructors

`shapes.Block()`, `shapes.Circle()`, `shapes.Rectangle()`. No lowercase factory
functions. Past bug: `wires.py` used `shapes.circle()` — fixed to
`shapes.Circle()`.

## Debugging nested diagram crashes

If a child diagram (with `parent=`) silently kills Python:

1. Grep for `exit()`/`quit()` in non-CLI code.
2. Try `import od_do.placement` before creating diagrams — if this kills Python,
   the bug is in the placement/transform import chain.
3. The init sequence: `draw()` runs BEFORE placement registration. If `draw()`
   succeeds but process dies, bug is in placement/transform.
4. `transform.py` module-level constants (`R0`, `R90`) fire during import, not
   during use.

## Draw.io backend is adapted from drawpyo

`src/od_do/drawio/` is copied from
[drawpyo](https://github.com/MerrimanInd/drawpyo) (MIT, v0.2.2). Only the XML
primitives were copied — no edges, connectors, groups, or shape libraries. od-do
uses its own shape system. If you're modifying drawio/ code, check drawpyo's
original for context.
