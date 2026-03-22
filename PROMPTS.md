# Test Prompts — FastAPI

## Prompt 1: Normal (route + OpenAPI)

> Add a new endpoint `GET /health` that returns `{"status": "ok"}` and is excluded from the OpenAPI docs. Add it to a separate `APIRouter` in a new file `fastapi/routes/health.py` and include it in the main `FastAPI` app setup.

**What this tests:** Basic router composition knowledge. With context-md, the agent can read `routing/registration_and_composition.md` and `openapi_docs/docs_endpoints.md` to learn about `include_in_schema`. Without, it needs to grep for patterns.

---

## Prompt 2: Architectural (yield dependency + scoping)

> I want to add a request-level rate limiter that works as a dependency. It should track request counts per client IP using an in-memory dict, and raise `HTTPException(429)` when the limit is exceeded. It needs to clean up its tracking state after each request completes, even if the endpoint raises an error. Implement this as a yield dependency in a new file `fastapi/dependencies/rate_limit.py` and add a test in `tests/test_rate_limit.py` that verifies the cleanup happens.

**What this tests:** Understanding of yield dependencies, request vs function scope, AsyncExitStack lifecycle, and `dependency_overrides` for testing. This is where hierarchy matters — the agent needs `dependency_injection/resolution_flow.md`, then drill into `scoping_and_caching/exit_stack_lifecycle.md`.

---

## Prompt 3: Cross-cutting (middleware + parameter handling)

> Add a custom middleware that logs the total number of validated request parameters (path + query + body fields) for each request. The count should be available as a response header `X-Param-Count`. Don't count internal framework params like `request` or `response`.

**What this tests:** Requires understanding both the middleware stack ordering (`request_pipeline/middleware_stack.md`) and how parameters are classified and counted (`parameter_handling/classification.md`). Cross-cutting concern that spans multiple CONTEXT folders.

---

## Prompt 4: Security (OAuth2 scope wiring)

> Add a new security dependency `require_scope(scope_name: str)` that returns a dependency function which checks that the current user's token includes the given scope. Wire it so that the required scopes show up correctly in the OpenAPI docs Authorize dialog. Add it to `fastapi/security/scopes.py`.

**What this tests:** OAuth2 scope propagation through the dependency tree, the `Security()` vs `Depends()` distinction, and how security definitions get into OpenAPI. Requires `security/scope_propagation.md` and `openapi_docs/schema_generation.md`.

---

## Prompt 5: Starlette boundary (vendored code modification)

> The `request_response()` function in `routing.py` is a vendored copy from Starlette. I need to add a hook that fires after dependency resolution but before the endpoint function runs. Where exactly should this go and what would the implementation look like? Write the code.

**What this tests:** Understanding of what's vendored and why (`starlette_relationship/vendored_code.md`), plus the request flow (`request_pipeline/request_flow.md`). Without context, the agent might not realize this is a vendored copy and might try to subclass instead.
