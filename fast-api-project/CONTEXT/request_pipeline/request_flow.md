---
description: End-to-end request lifecycle from ASGI entry to response — the critical path through get_request_handler()
---

# Request Flow

## Entry

`FastAPI.__call__()` sets `root_path` on the ASGI scope, then delegates to
`Starlette.__call__()` which passes the request through the middleware stack.

## Route matching

Starlette's `Router` iterates `self.routes`, calling `route.matches(scope)` on each.
The first match sets `scope["route"]` and `scope["path_params"]`.

## Endpoint execution

The matched `APIRoute`'s ASGI app is the return value of `get_request_handler()` in
`routing.py`. This is the critical function (~380 lines):

1. **Body reading** — reads JSON or form data. Form data gets an `AsyncExitStack` for
   file handle cleanup. Strict content-type checking is on by default (CSRF protection).

2. **Dependency resolution** — calls `solve_dependencies()` which recursively resolves
   the entire dependency tree, extracting params from the request along the way.

3. **Endpoint call** — runs the user's endpoint function with resolved values.
   Generator endpoints are detected and wrapped for streaming (SSE/JSONL).

4. **Response validation** — if `response_model` is set, the return value is validated
   against the Pydantic model. Validation errors at this stage are server errors (500),
   not client errors (422).

5. **Response construction** — serializes via `jsonable_encoder()`, applies status code,
   headers, and background tasks.

## Error context

On failure, FastAPI includes the endpoint's file path, line number, and function name
in the error message. This info is cached in `_endpoint_context_cache` (populated via
`inspect`) to avoid repeated filesystem access.
