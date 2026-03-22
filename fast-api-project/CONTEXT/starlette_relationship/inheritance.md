---
description: What FastAPI inherits vs adds on top of Starlette — the boundary between the two frameworks
---

# Starlette Inheritance

## What comes from Starlette

- ASGI application lifecycle
- `Request`, `Response`, `WebSocket` objects
- `Route` and `Router` for path matching and dispatch
- `TestClient` (re-exported as `fastapi.testclient.TestClient`)
- `ServerErrorMiddleware`, `ExceptionMiddleware`
- `StaticFiles`, `HTMLResponse`, `JSONResponse`, `RedirectResponse`
- `BackgroundTask` / `BackgroundTasks`
- Lifespan context manager support
- WebSocket handling
- `StreamingResponse`, `FileResponse`

## What FastAPI adds

- **Dependency injection** — entire `dependencies/` module
- **Automatic parameter extraction** — path/query/body/header/cookie from type hints
- **Pydantic validation** — automatic request validation and response serialization
- **OpenAPI generation** — `openapi/` module, docs endpoints
- **Security helpers** — `security/` module (OAuth2, API keys, HTTP auth)
- **Response model validation** — validating endpoint return values against Pydantic models
- **The `Annotated` parameter pattern** — `Query()`, `Path()`, `Body()`, etc.

## Key principle

FastAPI is a thin layer that adds automatic schema generation and dependency injection
on top of Starlette's ASGI foundation. Understanding which layer owns a behavior
tells you where to look: request/response handling → Starlette, parameter extraction
and DI → FastAPI.
