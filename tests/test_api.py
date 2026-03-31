import os
os.environ.setdefault("API_KEY", "test-key-for-tests")

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.ghasper_bi.main import app, API_KEY


client = TestClient(app)


def auth_header():
    return {"X-API-Key": API_KEY}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_trigger_refresh_requires_auth():
    response = client.post("/refresh")
    assert response.status_code == 401


def test_trigger_refresh_with_auth():
    with patch(
        "src.ghasper_bi.main.powerbi_client.trigger_refresh",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = client.post("/refresh", headers=auth_header())
    assert response.status_code == 200
    assert response.json()["status"] == "refresh_triggered"


def test_trigger_refresh_returns_502_on_failure():
    with patch(
        "src.ghasper_bi.main.powerbi_client.trigger_refresh",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = client.post("/refresh", headers=auth_header())
    assert response.status_code == 502
