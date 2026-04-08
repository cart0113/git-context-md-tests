---
description: How routes are registered via decorators, how include_router() merges routers, and the full parameter threading chain for adding new route options
---

# Route Registration and Composition

## Decorator flow

`@app.get("/items")` calls `APIRouter.add_api_route()`
(`fastapi/routing.py:1346`):

1. Creates an `APIRoute` instance (`fastapi/routing.py:817`) with the endpoint
2. `APIRoute.__init__()` (`fastapi/routing.py:818`) calls `get_dependant()` to
   introspect the function signature
3. The signature is flattened via `get_flat_dependant()` into a single
   `Dependant`
4. The route's ASGI app is built by `request_response()`
   (`fastapi/routing.py:97`) wrapping `get_request_handler()`
   (`fastapi/routing.py:351`)
5. Route is appended to `self.routes`

## Parameter threading chain

When adding a new parameter to `get_request_handler()`, it must be threaded
through the full registration path. All of these must accept and forward the
parameter:

1. `get_request_handler()` — `fastapi/routing.py:351` (receives and uses it)
2. `APIRoute.__init__()` — `fastapi/routing.py:818` (stores it as `self.X`)
3. `APIRoute.get_route_handler()` — `fastapi/routing.py:987` (passes
   `self.X` to `get_request_handler()`)
4. `APIRouter.add_api_route()` — `fastapi/routing.py:1346` (passes to
   `APIRoute()`)
5. HTTP method decorators on `APIRouter` — these call `add_api_route()`:
   - `.get()` at `fastapi/routing.py:1841`
   - `.put()` at `fastapi/routing.py:2218`
   - `.post()` at `fastapi/routing.py:2600`
   - `.delete()` at `fastapi/routing.py:2982`
   - `.options()` at `fastapi/routing.py:3359`
   - `.head()` at `fastapi/routing.py:3736`
   - `.patch()` at `fastapi/routing.py:4118`
   - `.trace()` at `fastapi/routing.py:4500`
6. Corresponding methods on `FastAPI` in `fastapi/applications.py` delegate to
   the router, so they also need the parameter if users should pass it via
   `@app.get(...)`.

Skipping any level means the parameter can't be set from that level's API. For
example, adding to `get_request_handler()` and `APIRoute` but not
`add_api_route()` means users can't pass it via decorators.

## Router composition

`include_router(router, prefix="/api")` (`fastapi/applications.py:1362`)
merges routes:

- Prefixes all paths
- Merges `dependencies` (router-level deps prepended to route-level deps)
- Merges `tags`, `responses`, `callbacks`
- Each route is re-wrapped — not shared by reference

The same `APIRouter` can be included multiple times with different prefixes, and
each inclusion gets its own independent copies of the routes.

## Path matching

Delegated entirely to Starlette's `compile_path()` which builds a regex from
the path template (e.g., `/items/{item_id}` → regex with named groups). Path
parameter type converters (`int`, `float`, `path`) are Starlette's
`param_convertors`.
