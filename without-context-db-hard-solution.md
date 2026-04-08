# Solution: `before_endpoint` Hook in `request_response()` / `get_request_handler()`

## Problem

Add a hook that fires after dependency resolution but before the endpoint function runs in FastAPI's vendored copy of Starlette's `request_response()` flow.

## Where It Goes

The hook fires inside `get_request_handler()`'s inner `app()` function in `fastapi/routing.py`. The exact insertion point is **after** `solve_dependencies()` returns and the error check passes (line ~467), but **before** any of the three endpoint execution branches (SSE stream, JSON stream, or regular `run_endpoint_function`).

The flow is:

```
request_response()
  └─ wrap_app_handling_exceptions()
       └─ get_request_handler() inner app()
            ├─ body parsing
            ├─ solve_dependencies()        ← dependencies resolved here
            ├─ error check
            ├─ **>>> HOOK FIRES HERE <<<**
            ├─ SSE stream branch (dependant.call(**solved_result.values))
            ├─ JSON stream branch (run_endpoint_function)
            └─ regular branch (run_endpoint_function)
```

## Implementation (3 changes to `fastapi/routing.py`)

### Change 1: Add `before_endpoint` parameter to `get_request_handler()`

```python
def get_request_handler(
    dependant: Dependant,
    body_field: ModelField | None = None,
    status_code: int | None = None,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    response_field: ModelField | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    dependency_overrides_provider: Any | None = None,
    embed_body_fields: bool = False,
    strict_content_type: bool | DefaultPlaceholder = Default(True),
    stream_item_field: ModelField | None = None,
    is_json_stream: bool = False,
    before_endpoint: Callable[[Request, dict[str, Any]], Awaitable[None]] | None = None,  # NEW
) -> Callable[[Request], Coroutine[Any, Any, Response]]:
```

### Change 2: Insert the hook call after dependency resolution

Inside `get_request_handler`'s inner `app()`, right after the error check on `solved_result.errors`:

```python
        errors = solved_result.errors
        assert dependant.call  # For types
        if not errors:
            if before_endpoint is not None:                         # NEW
                await before_endpoint(request, solved_result.values) # NEW
            # Shared serializer for stream items (JSONL and SSE).
            # ...rest of endpoint execution branches...
```

This placement ensures:
- Dependencies are fully resolved (including `yield` dependencies whose setup phase has run)
- Validation errors have been checked — the hook only fires on valid requests
- The hook runs before ALL endpoint code paths (SSE, JSONL stream, and regular)
- The hook receives the resolved `values` dict, so it can inspect/modify injected dependencies

### Change 3: Thread through `APIRoute`

In `APIRoute.__init__`, add the parameter and store it:

```python
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        # ...existing params...
        strict_content_type: bool | DefaultPlaceholder = Default(True),
        before_endpoint: Callable[[Request, dict[str, Any]], Awaitable[None]] | None = None,  # NEW
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.before_endpoint = before_endpoint  # NEW
```

In `APIRoute.get_route_handler`, pass it through:

```python
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        return get_request_handler(
            # ...existing args...
            stream_item_field=self.stream_item_field,
            is_json_stream=self.is_json_stream,
            before_endpoint=self.before_endpoint,  # NEW
        )
```

## Usage Example

```python
from fastapi import FastAPI, Request

app = FastAPI()

async def my_hook(request: Request, resolved_deps: dict[str, Any]) -> None:
    # Runs after all dependencies are resolved, before endpoint executes
    print(f"Endpoint about to run for {request.url.path}")
    print(f"Resolved dependencies: {list(resolved_deps.keys())}")
    # Could log, set request state, enforce policies, etc.

@app.get("/items/{item_id}", before_endpoint=my_hook)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    return {"item_id": item_id}
```

Note: `Awaitable` is already imported at line 9 of `routing.py` from `collections.abc`, so no new imports are needed.
