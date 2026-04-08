---
description: The two-AsyncExitStack design — why FastAPI maintains separate request-scoped and function-scoped stacks for dependency cleanup
---

# AsyncExitStack Lifecycle

FastAPI maintains **two** `AsyncExitStack` instances per request, stored in the
ASGI scope:

- `fastapi_inner_astack` — request-scoped dependencies (cleanup after response
  is sent)
- `fastapi_function_astack` — function-scoped dependencies (cleanup after
  endpoint returns, before response)

## Why two stacks?

A dependency with `yield` (a context manager pattern) needs its cleanup code to
run at the right time. Consider a database session dependency:

- **Request scope** (default): the session stays open through the entire
  request, including response serialization. Cleanup runs after the response is
  fully sent.
- **Function scope** (`Depends(get_db, scope="function")`): the session closes
  as soon as the endpoint function returns, before the response is serialized.

This matters for streaming responses — a function-scoped DB connection would
close before streaming completes, while request-scoped stays open.

## Implementation

`request_response()` (`fastapi/routing.py:97`) creates both stacks and adds
them to `scope`. `solve_dependencies()` (`fastapi/dependencies/utils.py:598`)
checks each dependency's `scope` attribute and enters the generator into the
appropriate stack via `_solve_generator()` (`fastapi/dependencies/utils.py:578`).

The stacks are closed in order: function stack first (inside the endpoint),
then request stack (in middleware via `AsyncExitStackMiddleware` added by
`build_middleware_stack()` in `fastapi/applications.py`).
