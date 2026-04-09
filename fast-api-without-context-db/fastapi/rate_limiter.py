"""Request-level rate limiter implemented as a yield dependency.

Tracks request counts per client IP using an in-memory dict and raises
HTTPException(429) when the limit is exceeded. Cleanup of tracking state
happens after each request completes, regardless of whether the endpoint
raised an error.
"""

import time

import fastapi


_request_counts: dict[str, list[float]] = {}


async def rate_limiter(request: fastapi.Request):
    client_ip = request.client.host
    now = time.monotonic()
    window = request.app.state.rate_limit_window
    max_requests = request.app.state.rate_limit_max_requests

    timestamps = _request_counts.setdefault(client_ip, [])
    timestamps[:] = [t for t in timestamps if now - t < window]

    if len(timestamps) >= max_requests:
        raise fastapi.HTTPException(status_code=429, detail="Rate limit exceeded")

    timestamps.append(now)
    try:
        yield
    finally:
        timestamps = _request_counts.get(client_ip, [])
        timestamps[:] = [t for t in timestamps if now - t < window]
        if not timestamps:
            _request_counts.pop(client_ip, None)
