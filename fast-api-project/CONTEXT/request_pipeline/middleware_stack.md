---
description: Middleware ordering — ServerErrorMiddleware, user middleware, ExceptionMiddleware, AsyncExitStackMiddleware, and why the order matters
---

# Middleware Stack

`build_middleware_stack()` in `applications.py` assembles middleware in this order
(outermost first):

```
ServerErrorMiddleware          ← catches unhandled exceptions, returns 500
  ↓
User middleware                ← added via app.add_middleware()
  ↓
ExceptionMiddleware            ← dispatches to @app.exception_handler() handlers
  ↓
AsyncExitStackMiddleware       ← closes request-scoped dependency stacks
  ↓
Router                         ← matches route and calls endpoint
```

## Why this order matters

- `ServerErrorMiddleware` is outermost so even middleware crashes return a proper 500
- User middleware runs before exception handling, so it can modify requests/responses
  but unhandled exceptions from user middleware get caught by ServerErrorMiddleware
- `ExceptionMiddleware` is inside user middleware, so `@app.exception_handler()` responses
  pass through user middleware (e.g., CORS headers get added to error responses)
- `AsyncExitStackMiddleware` is innermost so dependency cleanup happens after the
  response is fully sent but before exception middleware processes errors

This is a **customization** from Starlette's default ordering — FastAPI specifically
places `AsyncExitStackMiddleware` inside `ExceptionMiddleware` to ensure dependency
cleanup works correctly with exception handlers.
