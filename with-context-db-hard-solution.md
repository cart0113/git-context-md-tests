# Solution: `before_endpoint` hook in vendored `request_response()` pipeline

## Problem

Add a hook that fires after dependency resolution but before the endpoint
function runs in FastAPI's vendored `request_response()` pipeline.

## Where the hook goes

The insertion point is inside `get_request_handler()` in `fastapi/routing.py`,
at the `if not errors:` branch (line 469). This is the single choke point where:

- Dependencies are fully resolved (`solve_dependencies()` returned)
- Validation passed (no errors)
- The endpoint function has **not** been called yet

All four endpoint call paths (SSE stream, JSONL stream, raw streaming, regular)
branch from this point, so the hook covers every case.

## Implementation — 3 changes in `fastapi/routing.py`

### 1. `get_request_handler()` signature (line 351)

Added an optional `before_endpoint` callback parameter:

```python
def get_request_handler(
    dependant: Dependant,
    body_field: ModelField | None = None,
    # ... existing params ...
    is_json_stream: bool = False,
    before_endpoint: Callable[[Request, dict[str, Any]], Awaitable[None] | None]
    | None = None,
) -> Callable[[Request], Coroutine[Any, Any, Response]]:
```

The callback signature is `(request, solved_values) -> None | Awaitable[None]`.
It receives the `Request` and the dict of resolved dependency values. Both sync
and async callables are supported.

### 2. Hook invocation inside `app()` (after line 469)

Inserted immediately after `if not errors:` and before the endpoint call
branches:

```python
        if not errors:
            if before_endpoint is not None:
                result = before_endpoint(request, solved_result.values)
                if inspect.isawaitable(result):
                    await result
            # ... existing endpoint call branches (SSE, JSONL, raw, regular) ...
```

`inspect.isawaitable()` is used (already imported) to handle both sync and async
hooks without requiring the caller to always provide a coroutine.

### 3. `APIRoute.__init__()` and `get_route_handler()` (lines 817, 987)

Threaded the parameter through `APIRoute`:

**`__init__` signature** — added at the end of the keyword args:

```python
class APIRoute(routing.Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        # ... existing params ...
        strict_content_type: bool | DefaultPlaceholder = Default(True),
        before_endpoint: Callable[[Request, dict[str, Any]], Awaitable[None] | None]
        | None = None,
    ) -> None:
```

**`__init__` body** — stores it:

```python
        self.before_endpoint = before_endpoint
```

**`get_route_handler()`** — passes it through:

```python
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        return get_request_handler(
            # ... existing kwargs ...
            is_json_stream=self.is_json_stream,
            before_endpoint=self.before_endpoint,
        )
```

## Usage example

```python
from fastapi import FastAPI, Request

async def log_resolved_deps(request: Request, values: dict) -> None:
    print(f"{request.method} {request.url.path} resolved: {list(values.keys())}")

app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

# Override the route's before_endpoint hook
for route in app.routes:
    if hasattr(route, "before_endpoint"):
        route.before_endpoint = log_resolved_deps
        # Rebuild the ASGI app to pick up the new handler
        route.app = route.__class__.request_response(route.get_route_handler())
```

Or set it at route registration time by subclassing `APIRoute`:

```python
from fastapi.routing import APIRoute

class HookedRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("before_endpoint", log_resolved_deps)
        super().__init__(*args, **kwargs)

app = FastAPI()
app.router.route_class = HookedRoute
```

## Why this approach

- **Single insertion point**: All four endpoint branches (SSE, JSONL, raw
  stream, regular) originate after `if not errors:`, so one hook covers them all.
- **Sync + async support**: `inspect.isawaitable()` avoids forcing async on
  callers who don't need it.
- **No default cost**: When `before_endpoint is None` (the default), it's a
  single falsy check — zero overhead for existing routes.
- **Follows existing patterns**: The parameter threading through
  `get_request_handler` -> `APIRoute.__init__` -> `get_route_handler` matches
  how every other option (e.g., `strict_content_type`, `dependency_overrides_provider`)
  flows through the same path.
