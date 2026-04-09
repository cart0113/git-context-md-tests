---
description: Non-obvious behaviors that are correct but surprising — body embedding, cache keys, schema caching, scope restrictions
---

# Gotchas

## Body embedding shape change

Adding a second body parameter to an endpoint silently changes the request
schema from flat (`{"name": "foo"}`) to nested
(`{"item": {"name": "foo"}, "user": {...}}`). OpenAPI docs update but clients
break. Check `_should_embed_body_fields()` in `fastapi/dependencies/utils.py`.

## Dependency cache key includes OAuth scopes

The cache key is `(callable, tuple(scopes), scope)`. The same dependency
function resolves separately when used with different `Security()` scopes.
This is in `solve_dependencies()` in `fastapi/dependencies/utils.py`.

## OpenAPI schema caching

The generated spec is cached on `app.openapi_schema` after the first
`/openapi.json` request. Routes added after that won't appear until you clear
the cache (`app.openapi_schema = None`).

## Generator scope restrictions

A request-scoped generator dependency cannot depend on a function-scoped
dependency. `get_dependant()` raises `DependencyScopeError` for this case.
The request-scoped generator outlives the function scope, so its
function-scoped dependency would already be cleaned up.

## Strict content-type is on by default

`strict_content_type=True` (default) rejects requests without a proper
`content-type` header. This is intentional CSRF protection but surprises
people testing with curl without `-H "Content-Type: application/json"`.
