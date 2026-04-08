"""Request-level rate limiter implemented as a yield dependency.

Tracks request counts per client IP using an in-memory dict and raises
``HTTPException(429)`` when the limit is exceeded.  Cleanup of tracking state
happens after each request completes, regardless of whether the endpoint (or
the limiter itself) raised an error.
"""

from collections import defaultdict
from typing import Any, Generator

from fastapi import HTTPException, Request


_request_counts: dict[str, int] = defaultdict(int)


def rate_limiter(
    max_requests: int = 10,
) -> Any:
    """Return a yield dependency that enforces a per-IP request limit.

    Args:
        max_requests: Maximum concurrent in-flight requests allowed per
            client IP.
    """

    def dependency(request: Request) -> Generator[None, None, None]:
        client_ip = request.client.host if request.client else "unknown"
        _request_counts[client_ip] += 1
        try:
            if _request_counts[client_ip] > max_requests:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded"
                )
            yield
        finally:
            _request_counts[client_ip] -= 1
            if _request_counts[client_ip] <= 0:
                del _request_counts[client_ip]

    return dependency
