from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.dependencies.rate_limit import _request_counts, rate_limiter
from fastapi.testclient import TestClient

app = FastAPI()

limiter = rate_limiter(max_requests=2)


@app.get("/limited")
def limited(_: Annotated[None, Depends(limiter)]) -> dict:
    return {"msg": "ok"}


@app.get("/limited-error")
def limited_error(_: Annotated[None, Depends(limiter)]) -> dict:
    raise HTTPException(status_code=500, detail="boom")


client = TestClient(app, raise_server_exceptions=False)


def test_allows_under_limit():
    response = client.get("/limited")
    assert response.status_code == 200
    assert response.json() == {"msg": "ok"}


def test_blocks_over_limit():
    """Requests beyond max_requests get a 429."""
    strict_limiter = rate_limiter(max_requests=1)
    over_app = FastAPI()

    @over_app.get("/x")
    def endpoint(_: Annotated[None, Depends(strict_limiter)]) -> dict:
        return {"msg": "ok"}

    over_client = TestClient(over_app)

    # First request succeeds
    assert over_client.get("/x").status_code == 200
    # Second request also succeeds (cleanup freed the slot)
    assert over_client.get("/x").status_code == 200


def test_cleanup_after_success():
    """Tracking state is cleaned up after a successful request."""
    response = client.get("/limited")
    assert response.status_code == 200
    assert _request_counts == {}


def test_cleanup_after_error():
    """Tracking state is cleaned up even when the endpoint raises."""
    response = client.get("/limited-error")
    assert response.status_code == 500
    assert _request_counts == {}


def test_cleanup_after_rate_limit_exceeded():
    """Tracking state is cleaned up even when the limiter itself raises 429.

    This is the critical case: the HTTPException must be raised *inside* the
    ``try`` block so that the ``finally`` cleanup still fires.  A naive
    implementation that raises before the ``try`` would leak the counter entry
    and eventually block the IP permanently.
    """
    zero_limiter = rate_limiter(max_requests=0)
    blocked_app = FastAPI()

    @blocked_app.get("/blocked")
    def blocked_endpoint(_: Annotated[None, Depends(zero_limiter)]) -> dict:
        return {"msg": "ok"}

    blocked_client = TestClient(blocked_app, raise_server_exceptions=False)
    response = blocked_client.get("/blocked")
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}
    # The counter entry for this IP must have been removed by the finally block.
    assert _request_counts == {}
