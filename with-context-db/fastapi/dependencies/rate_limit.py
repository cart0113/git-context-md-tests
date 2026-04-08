from collections import defaultdict
from typing import Generator

from fastapi import HTTPException, Request

_active_requests: dict[str, int] = defaultdict(int)


def get_rate_limiter(limit: int = 1):
    """Factory returning a yield dependency that limits concurrent requests per client IP."""

    def rate_limit(request: Request) -> Generator[None, None, None]:
        ip = request.client.host if request.client else "unknown"
        _active_requests[ip] += 1
        if _active_requests[ip] > limit:
            _active_requests[ip] -= 1
            raise HTTPException(status_code=429, detail="Too Many Requests")
        try:
            yield
        finally:
            _active_requests[ip] -= 1
            if _active_requests[ip] == 0:
                del _active_requests[ip]

    return rate_limit
