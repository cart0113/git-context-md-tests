---
description: Why things are the way they are — vendored code, two exit stacks, middleware ordering. Rationale not visible in the code itself.
---

# Design Decisions

## Why request_response() is vendored from Starlette

`request_response()` in `fastapi/routing.py` is a copy of Starlette's
version. It's vendored (not subclassed) because it's a module-level function,
not a method — can't be overridden via inheritance. FastAPI needs to inject
`AsyncExitStack` creation into the middle of the function. The code comment on
the function says this, but the deeper implication is: any changes to this
function must be manually kept in sync with upstream Starlette.

## Why two AsyncExitStacks per request

FastAPI creates `fastapi_inner_astack` (request-scoped) and
`fastapi_function_astack` (function-scoped) in the ASGI scope. This is for
`yield` dependencies — a request-scoped DB session stays open through response
serialization and streaming, while a function-scoped one closes when the
endpoint returns. Without two stacks, you can't have both behaviors.

## Why the middleware order matters

```
ServerErrorMiddleware → User middleware → ExceptionMiddleware
  → AsyncExitStackMiddleware → Router
```

Key consequence: `ExceptionMiddleware` is inside user middleware, so
`@app.exception_handler()` responses pass through user middleware (e.g., CORS
headers get added to error responses). `AsyncExitStackMiddleware` is innermost
so dependency cleanup happens after response is sent.

## Why body params get embedded

When an endpoint has multiple body params, they're wrapped in a synthetic
object so each param has a key. This is by design — there's no other way to
distinguish which JSON fields belong to which param. See `gotchas.md` for why
this surprises people. Logic is in `_should_embed_body_fields()` in
`fastapi/dependencies/utils.py`.
