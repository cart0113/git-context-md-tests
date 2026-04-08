---
description: How analyze_param() at fastapi/dependencies/utils.py:393 decides if a parameter is path, query, body, header, cookie, or a dependency
---

# Parameter Classification

`analyze_param()` (`fastapi/dependencies/utils.py:393`) classifies each
endpoint parameter. Called from `get_dependant()` (line 286) during startup.

## Decision order

1. **Annotated with Depends()** → sub-dependency (not a param, recurse into it)
2. **Annotated with Body/Form/File** → body parameter
3. **Annotated with Header** → header parameter (underscores converted to
   dashes)
4. **Annotated with Cookie** → cookie parameter
5. **Annotated with Path** → path parameter
6. **Annotated with Query** → query parameter
7. **Name matches a path template variable** → path parameter (implicit)
8. **Is a Pydantic model or complex type** → body parameter (implicit)
9. **Otherwise** → query parameter (default)

## Implicit classification

A parameter with no annotation marker gets classified by its type:

```python
# These are both query params (simple types, no annotation):
def endpoint(name: str, count: int = 10): ...

# This is implicitly a body param (Pydantic model):
def endpoint(item: Item): ...

# This is explicitly a path param (matches path template):
@app.get("/items/{item_id}")
def endpoint(item_id: int): ...
```

## The Annotated pattern

Modern FastAPI uses `Annotated[type, metadata]`:

```python
def endpoint(item_id: Annotated[int, Path(ge=1)]): ...
```

`analyze_param()` unpacks `Annotated` and finds the `FieldInfo` subclass in
metadata. Multiple `FieldInfo` in one `Annotated` is an error.
