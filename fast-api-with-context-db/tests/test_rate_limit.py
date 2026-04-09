from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from fastapi.dependencies.rate_limit import _active_requests, get_rate_limiter

app = FastAPI()

rate_limit = get_rate_limiter(limit=1)


@app.get("/guarded")
def guarded(_: Annotated[None, Depends(rate_limit)]) -> Any:
    return {"ok": True}


@app.get("/guarded-raises")
def guarded_raises(_: Annotated[None, Depends(rate_limit)]) -> Any:
    raise HTTPException(status_code=500, detail="endpoint error")


client = TestClient(app, raise_server_exceptions=False)


def setup_function():
    _active_requests.clear()


def test_request_within_limit_succeeds():
    response = client.get("/guarded")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_cleanup_after_successful_request():
    client.get("/guarded")
    assert "testclient" not in _active_requests


def test_cleanup_after_endpoint_raises():
    client.get("/guarded-raises")
    assert "testclient" not in _active_requests


def test_concurrent_limit_exceeded_returns_429():
    # Simulate a stuck concurrent request by manually pre-incrementing the counter
    _active_requests["testclient"] = 1
    response = client.get("/guarded")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}


def test_counter_restored_after_429():
    _active_requests["testclient"] = 1
    client.get("/guarded")
    # The rejected request must not leave a leaked increment
    assert _active_requests["testclient"] == 1
