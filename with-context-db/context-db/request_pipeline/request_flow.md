---
description: End-to-end request lifecycle from ASGI entry to response — the critical path through get_request_handler() at fastapi/routing.py:351
---

# Request Flow

## Entry

`FastAPI.__call__()` (`fastapi/applications.py:41`) sets `root_path` on the
ASGI scope, then delegates to `Starlette.__call__()` which passes the request
through the middleware stack.

## Route matching

Starlette's `Router` iterates `self.routes`, calling `route.matches(scope)` on
each. The first match sets `scope["route"]` and `scope["path_params"]`.

## Endpoint execution — `get_request_handler()` at `fastapi/routing.py:351`

The matched `APIRoute`'s ASGI app is the return value of
`get_request_handler()`. This is the critical function. Its inner `app()`
coroutine (`fastapi/routing.py:384`) runs:

1. **Body reading** — reads JSON or form data. Form data gets an
   `AsyncExitStack` for file handle cleanup. Strict content-type checking is on
   by default (CSRF protection).

2. **Dependency resolution** — `solve_dependencies()` call at
   `fastapi/routing.py:459` recursively resolves the entire dependency tree,
   extracting params from the request along the way.

3. **Error check** — `if not errors:` at `fastapi/routing.py:469`. Everything
   after this point is guarded by successful validation.

4. **Endpoint call** — four branches:
   - SSE stream: `fastapi/routing.py:502` (`if is_sse_stream:`)
   - JSONL stream: `fastapi/routing.py:626` (`elif is_json_stream:`)
   - Raw generator stream: `fastapi/routing.py:659`
     (`elif dependant.is_async_gen_callable or dependant.is_gen_callable:`)
   - Regular response: `fastapi/routing.py:679` (`else:`)

5. **Response validation** — if `response_model` is set, the return value is
   validated against the Pydantic model. Validation errors here are server
   errors (500), not client errors (422).

6. **Response construction** — serializes via `jsonable_encoder()`, applies
   status code, headers, and background tasks.

## Helper: `run_endpoint_function()` at `fastapi/routing.py:320`

Runs the user's endpoint callable — dispatches sync functions to a threadpool
via `run_in_threadpool()`, awaits async functions directly.

## Error context

On failure, FastAPI includes the endpoint's file path, line number, and function
name in the error message. This info is cached in `_endpoint_context_cache`
(populated via `inspect`) to avoid repeated filesystem access.
