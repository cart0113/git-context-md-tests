---
description:
  Known bugs, past fixes, and debugging patterns — exit() in module-level code,
  case sensitivity, nested diagram crash diagnosis
---

# Known Bugs and Fixes

## CRITICAL: Never put exit() or sys.exit() in module-level code paths

**Date:** 2026-04-06

**Bug:** `exit()` was accidentally left in `Transform.__init__()` in
`transform.py`. Because `transform.py` defines module-level constants like
`R0 = Transform(rotation=0)`, the `exit()` fired during module import, silently
killing Python.

**Symptom:** Any code that triggers `from od_do.placement import ...` would
cause Python to terminate with no error message. This looked like a segfault or
infinite recursion, but was actually a clean `exit()`. The placement module
imports transform, which instantiates Transform constants at module level.

**Why it was hard to find:**

- No traceback, no error message — `exit()` exits cleanly
- The import is deferred (inside `Diagram.__init__` at placement registration
  time), so it only fires when a child diagram is nested in a parent
- Standalone diagrams (no parent) and standalone Battery() work fine
- faulthandler doesn't catch `exit()` since it's not a crash
- Python process just stops mid-execution

**Fix:** Remove the stray `exit()` from `Transform.__init__`.

**Lesson:** Never put `exit()`, `sys.exit()`, or `quit()` in constructors,
especially in classes that have module-level constant instances.

## API name case: shapes.Circle not shapes.circle

**Date:** 2026-04-06

**Bug:** `wires.py` in the circuit elements library used `shapes.circle()`
(lowercase) but the shapes module exports `Circle` (class, uppercase).

**Fix:** Changed all `shapes.circle(` to `shapes.Circle(` in
`diagram_libs/basic_circuit_elements/wires.py` (5 occurrences).

**Pattern:** OD-DO uses class names (PascalCase) for all shape constructors:
`shapes.Block()`, `shapes.Circle()`, `shapes.Rectangle()`, etc. There are no
lowercase factory functions.

## Debugging nested diagram crashes

If a child diagram (with `parent=`) silently kills Python:

1. **Check for stray exit()/quit()** — grep the entire codebase for `exit()` and
   `quit()` in non-CLI code
2. **Check the import chain** — `Diagram.__init__` does a deferred import of
   `placement` at line ~151. If placement or its dependencies have issues, they
   only manifest when nesting diagrams
3. **The init sequence matters** — `draw()` runs BEFORE placement registration.
   If draw() succeeds but the process dies, the bug is in placement/transform
4. **Pre-import to isolate** — try `import od_do.placement` before creating any
   diagrams. If this kills Python, the bug is in placement's import chain
   (placement → transform → shapes.base)
5. **Module-level constants** — `transform.py` creates `R0`, `R90`, etc. at
   module level. Any bug in `Transform.__init__` fires during import, not during
   use
