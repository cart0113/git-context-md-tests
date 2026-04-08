---
description: How generator endpoints become streaming responses — SSE, JSONL, and raw streaming branches in get_request_handler() at fastapi/routing.py:351
---

# Streaming Responses

FastAPI detects generator endpoints and wraps them for streaming. Detection
happens in `get_request_handler()` (`fastapi/routing.py:351`) via the
`Dependant` model's `is_async_gen_callable` and `is_gen_callable` properties.

## The four endpoint branches after `if not errors:` (`fastapi/routing.py:469`)

1. **SSE stream** — `fastapi/routing.py:502` (`if is_sse_stream:`). Async
   generator endpoints returning EventSource-formatted data.
2. **JSONL stream** — `fastapi/routing.py:626` (`elif is_json_stream:`). Each
   yielded value is serialized to a JSON line.
3. **Raw generator stream** — `fastapi/routing.py:659`
   (`elif dependant.is_async_gen_callable or dependant.is_gen_callable:`).
   Streams raw bytes/strings.
4. **Regular response** — `fastapi/routing.py:679` (`else:`). Non-streaming,
   calls `run_endpoint_function()` (`fastapi/routing.py:320`).

All four branches share a common serializer `_serialize_data()` defined at
`fastapi/routing.py:477` for stream item validation.

This is distinct from explicitly returning a `StreamingResponse` — that
bypasses FastAPI's serialization entirely.
