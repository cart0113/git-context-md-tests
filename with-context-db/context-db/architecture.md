---
description: File map, class hierarchy, and which files own which concerns — start here to know where to look
---

# Architecture

## File map

- `fastapi/applications.py` — `FastAPI` class, `include_router()`, docs
  endpoint setup, middleware stack builder (see section map below)
- `fastapi/routing.py` — `APIRoute`, `APIRouter`, `get_request_handler()`,
  `request_response()`, HTTP method decorators (see section map below)
- `fastapi/dependencies/utils.py` — `solve_dependencies()`,
  `get_dependant()`, `analyze_param()`, parameter extraction and validation
- `fastapi/dependencies/models.py` — `Dependant` dataclass
- `fastapi/openapi/utils.py` — `get_openapi()` schema generation
- `fastapi/openapi/docs.py` — Swagger UI and ReDoc HTML rendering
- `fastapi/security/` — OAuth2, HTTP auth, API key classes

## Section map: `fastapi/routing.py` (~5000 lines)

- `routing.py:97` — `request_response()` (vendored from Starlette)
- `routing.py:320` — `run_endpoint_function()`
- `routing.py:351` — `get_request_handler()` (the critical request pipeline)
- `routing.py:817` — `APIRoute` class
- `routing.py:987` — `APIRoute.get_route_handler()`
- `routing.py:1015` — `APIRouter` class
- `routing.py:1346` — `APIRouter.add_api_route()`
- `routing.py:1841–4966` — HTTP method decorators (`.get()`, `.post()`, etc.)

## Section map: `fastapi/applications.py` (~4700 lines)

- `applications.py:41` — `FastAPI` class
- `applications.py:1362` — `include_router()`

## Class hierarchy

```
Starlette → FastAPI           (holds self.router: APIRouter)
starlette.Router → APIRouter  (DI, OpenAPI, response models)
starlette.Route → APIRoute    (Dependant analysis, validation)
```

`FastAPI` subclasses `Starlette`, NOT `APIRouter`. It delegates path
operations to an internal `self.router`.

## Request lifecycle (conceptual)

```
FastAPI.__call__() → middleware stack → Router → APIRoute.app
  → get_request_handler().app()
    → body parsing
    → solve_dependencies()
    → endpoint call (4 branches: SSE / JSONL / raw stream / regular)
    → response validation + construction
```

The critical function is `get_request_handler()` in `fastapi/routing.py`.
Everything from body parsing through response construction lives in its
inner `app()` coroutine.
