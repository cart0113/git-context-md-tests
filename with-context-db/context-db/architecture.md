---
description: File map, class hierarchy, and which files own which concerns — start here to know where to look
---

# Architecture

## File map

- `fastapi/applications.py` — `FastAPI` class (subclasses Starlette),
  `include_router()`, docs endpoint setup, middleware stack builder
- `fastapi/routing.py` — the big file. Contains `APIRoute`, `APIRouter`,
  `get_request_handler()` (the request pipeline), `request_response()`
  (vendored from Starlette), and all HTTP method decorators
- `fastapi/dependencies/utils.py` — `solve_dependencies()`,
  `get_dependant()`, `analyze_param()`, parameter extraction and validation
- `fastapi/dependencies/models.py` — `Dependant` dataclass (the dependency
  tree node)
- `fastapi/openapi/utils.py` — `get_openapi()` schema generation
- `fastapi/openapi/docs.py` — Swagger UI and ReDoc HTML rendering
- `fastapi/security/` — OAuth2, HTTP auth, API key classes (all are
  dependencies that extract credentials from requests)

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
