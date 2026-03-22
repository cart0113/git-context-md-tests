---
description: Class inheritance chain from Starlette Router through APIRouter to FastAPI, and what each layer adds
---

# Routing Class Hierarchy

```
starlette.routing.Router
  └── fastapi.routing.APIRouter          (adds DI, OpenAPI metadata, response models)
        └── fastapi.applications.FastAPI  (adds docs endpoints, middleware builder, openapi())
```

`FastAPI` does not directly subclass `APIRouter`. It subclasses `Starlette` and holds an
internal `self.router: APIRouter`. All path operation methods (`get()`, `post()`, etc.)
are defined on `APIRouter` and delegated from `FastAPI`.

Route-level classes:

```
starlette.routing.Route
  └── fastapi.routing.APIRoute          (adds Dependant analysis, response validation)

starlette.routing.WebSocketRoute
  └── fastapi.routing.APIWebSocketRoute (adds Dependant analysis for WebSocket)
```

## Key files

- `applications.py` — `FastAPI` class (~5K lines, mostly decorator method signatures)
- `routing.py` — `APIRouter`, `APIRoute`, `APIWebSocketRoute`, `get_request_handler()`
