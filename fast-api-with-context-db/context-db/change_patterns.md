---
description:
  Patterns for making changes — parameter threading chain, dependency scoping,
  testing with overrides. Read this before modifying the request pipeline.
---

# Change Patterns

## Adding a new parameter to the request pipeline

New parameters to `get_request_handler()` must be threaded through the full
registration chain. Missing any level means users can't set the parameter from
that level's API (e.g., can't pass it via `@app.get(...)` decorators).

The chain:

1. **`get_request_handler()`** in `fastapi/routing.py` — receives and uses it
2. **`APIRoute.__init__()`** in `fastapi/routing.py` — accepts and stores as
   `self.X`
3. **`APIRoute.get_route_handler()`** — passes `self.X` to
   `get_request_handler()`
4. **`APIRouter.add_api_route()`** — accepts and passes to `APIRoute()`
5. **HTTP method decorators** on `APIRouter` (`.get()`, `.post()`, `.put()`,
   `.delete()`, `.patch()`, `.options()`, `.head()`, `.trace()`) — all call
   `add_api_route()`, each needs the parameter
6. **Corresponding methods on `FastAPI`** in `fastapi/applications.py` —
   delegate to the router

Search for an existing parameter like `strict_content_type` to see the pattern
end-to-end. See `architecture.md` for line-level locations in the section map.

## Adding a new dependency scope

Dependencies can be `"request"` or `"function"` scoped. The scope determines
which `AsyncExitStack` the generator is entered on. The selection happens in
`solve_dependencies()` in `fastapi/dependencies/utils.py` — it checks
`sub_dependant.scope` and passes the appropriate stack to `_solve_generator()`.

## Testing with dependency_overrides

`app.dependency_overrides` looks up overrides by **identity** (the original
callable object), not by name. You must reference the exact same function object
used in `Depends()`. Overrides apply transitively.
