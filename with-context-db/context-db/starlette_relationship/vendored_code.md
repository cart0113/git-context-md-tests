---
description: Code vendored (copied) from Starlette into FastAPI — request_response(), lifespan wrappers, and why they were forked
---

# Vendored Starlette Code

FastAPI copies and modifies several pieces of Starlette code in
`fastapi/routing.py`:

## request_response() — `fastapi/routing.py:97`

The most important vendored piece. Starlette's `request_response()` creates an
ASGI app from an endpoint callable. FastAPI's version adds creation of
`fastapi_inner_astack` and `fastapi_function_astack` in the ASGI scope — these
`AsyncExitStack` instances are needed for dependency cleanup (yield
dependencies). Starlette's version doesn't know about FastAPI's dependency
lifecycle.

## Lifespan wrappers

- `_AsyncLiftContextManager` — wraps a generator-based lifespan into an async
  context manager
- `_wrap_gen_lifespan_context` — adapter for old-style generator lifespans
- `_DefaultLifespan` — default no-op lifespan

These are vendored for backward compatibility with deprecated Starlette lifespan
APIs.

## Why vendor instead of subclass?

These are module-level functions, not methods — they can't be overridden via
inheritance. FastAPI needs to inject its own behavior (the exit stacks) into the
middle of the function's logic, which requires modifying the code directly.

When modifying vendored code (e.g., adding a new parameter), the change must
be threaded through the full registration chain. See
`routing/registration_and_composition.md` for the complete parameter threading
path.
