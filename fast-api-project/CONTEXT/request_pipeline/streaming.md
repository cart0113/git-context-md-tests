---
description: How generator and async generator endpoints become streaming responses — SSE, JSONL, and raw streaming detection
---

# Streaming Responses

FastAPI detects generator endpoints and automatically wraps them for streaming:

- **Async generator** (`async def endpoint() -> AsyncGenerator`) → SSE / EventSource streaming
- **Sync generator** (`def endpoint() -> Generator`) → JSONL streaming

Detection happens in `get_request_handler()` via the `Dependant` model's
`is_async_gen_callable` and `is_gen_callable` properties.

The generator's yielded values are serialized individually and sent as chunks.
The response uses `StreamingResponse` from Starlette.

This is distinct from explicitly returning a `StreamingResponse` — that bypasses
FastAPI's serialization entirely and streams raw bytes/strings.
