---
description: How routes are registered via decorators, how include_router() merges routers, and how path operations are composed
---

# Route Registration and Composition

## Decorator flow

`@app.get("/items")` calls `APIRouter.add_api_route()`:

1. Creates an `APIRoute` instance with the endpoint callable
2. `APIRoute.__init__` calls `get_dependant()` to introspect the function signature
3. The signature is flattened via `get_flat_dependant()` into a single `Dependant`
4. The route's ASGI app is built by `request_response()` wrapping `get_request_handler()`
5. Route is appended to `self.routes`

## Router composition

`include_router(router, prefix="/api")` merges routes:

- Prefixes all paths
- Merges `dependencies` (router-level deps prepended to route-level deps)
- Merges `tags`, `responses`, `callbacks`
- Each route is re-wrapped — not shared by reference

This means the same `APIRouter` can be included multiple times with different prefixes,
and each inclusion gets its own independent copies of the routes.

## Path matching

Delegated entirely to Starlette's `compile_path()` which builds a regex from the path
template (e.g., `/items/{item_id}` → regex with named groups). Path parameter type
converters (`int`, `float`, `path`) are Starlette's `param_convertors`.
