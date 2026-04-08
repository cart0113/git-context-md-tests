---
description: Class inheritance chain from Starlette Router through APIRouter to FastAPI — what each layer adds, with file locations
---

# Routing Class Hierarchy

```
starlette.routing.Router
  └── fastapi.routing.APIRouter          fastapi/routing.py:1015
        └── fastapi.applications.FastAPI  fastapi/applications.py:41
```

`FastAPI` subclasses `Starlette`, not `APIRouter`. It holds an internal
`self.router: APIRouter`. All path operation methods (`get()`, `post()`, etc.)
are defined on `APIRouter` and delegated from `FastAPI`.

Route-level classes:

```
starlette.routing.Route
  └── fastapi.routing.APIRoute            fastapi/routing.py:817

starlette.routing.WebSocketRoute
  └── fastapi.routing.APIWebSocketRoute   fastapi/routing.py:1007
```

## Key functions in `fastapi/routing.py`

- `request_response()` — line 97 (vendored from Starlette)
- `run_endpoint_function()` — line 320
- `get_request_handler()` — line 351 (the critical ~380-line function)
- `APIRoute` — line 817
- `APIRoute.get_route_handler()` — line 987
- `APIRouter` — line 1015
- `APIRouter.add_api_route()` — line 1346

## Key files

- `fastapi/applications.py` — `FastAPI` class, `include_router()` at line 1362
- `fastapi/routing.py` — `APIRouter`, `APIRoute`, `get_request_handler()`
- `fastapi/dependencies/utils.py` — `solve_dependencies()` at line 598,
  `get_dependant()` at line 286, `analyze_param()` at line 393
- `fastapi/dependencies/models.py` — `Dependant` dataclass at line 32
