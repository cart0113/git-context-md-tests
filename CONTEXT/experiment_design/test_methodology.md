---
description: How to run tests — branch switching, test prompts, what to measure, and how to compare results
---

# Test Methodology

## Running a test

1. Check out the target branch (`with-context-md` or `without-context-md`)
2. Open Claude Code in the project subdirectory (e.g., `fast-api-project/`)
3. Ask the test prompt
4. Record: token usage, tool calls, time, answer quality

## Test prompts for FastAPI

### Prompt 1 (Normal)

> Add a new endpoint `GET /health` that returns `{"status": "ok"}` and is excluded from the OpenAPI docs. Add it to a separate `APIRouter` in a new file `fastapi/routes/health.py` and include it in the main `FastAPI` app setup.

### Prompt 2 (Architectural)

> I want to add a request-level rate limiter that works as a dependency. It should track request counts per client IP using an in-memory dict, and raise `HTTPException(429)` when the limit is exceeded. It needs to clean up its tracking state after each request completes, even if the endpoint raises an error. Implement this as a yield dependency in a new file `fastapi/dependencies/rate_limit.py` and add a test in `tests/test_rate_limit.py` that verifies the cleanup happens.

## Metrics

- **Token usage** — from Claude API usage stats
- **Tool calls** — count of Grep, Glob, Read, Bash calls before substantive answer
- **Time** — wall clock time to first useful response
- **Accuracy** — manual evaluation: did the agent get the architecture right?
- **Discovery** — did the agent find non-obvious context it wouldn't have grepped for?

## Comparing results

Run each prompt on both branches. Reset Claude Code context between runs (new session). Record results side-by-side.
