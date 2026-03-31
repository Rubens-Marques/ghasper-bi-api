import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from src.ghasper_bi.powerbi.client import PowerBIClient


def make_client():
    return PowerBIClient(
        client_id="test_id",
        client_secret="test_secret",
        tenant_id="test_tenant",
        workspace_id="ws_123",
        dataset_id="ds_456",
    )


@pytest.mark.asyncio
async def test_get_token_returns_access_token():
    client = make_client()
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "tok_abc123", "expires_in": 3600}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        token = await client.get_token()

    assert token == "tok_abc123"
    assert client._token == "tok_abc123"
    assert client._token_expires_at > time.time()


@pytest.mark.asyncio
async def test_get_token_sets_expiry_with_margin():
    client = make_client()
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "tok_abc123", "expires_in": 3600}
    mock_response.raise_for_status = MagicMock()

    before = time.time()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        await client.get_token()

    # expires_at deve ser ~3540s a partir de agora (3600 - 60 de margem)
    assert client._token_expires_at >= before + 3539
    assert client._token_expires_at <= before + 3541


@pytest.mark.asyncio
async def test_trigger_refresh_calls_correct_endpoint_with_auth():
    client = make_client()
    client._token = "tok_abc123"
    client._token_expires_at = time.time() + 3600  # token válido

    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        result = await client.trigger_refresh()

    assert result is True
    call_url = mock_post.call_args[0][0]
    assert "datasets/ds_456/refreshes" in call_url
    call_headers = mock_post.call_args[1]["headers"]
    assert call_headers["Authorization"] == "Bearer tok_abc123"


@pytest.mark.asyncio
async def test_trigger_refresh_renews_expired_token():
    client = make_client()
    client._token = "tok_old"
    client._token_expires_at = time.time() - 1  # token expirado

    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "tok_new", "expires_in": 3600}
    mock_token_response.raise_for_status = MagicMock()

    mock_refresh_response = MagicMock()
    mock_refresh_response.status_code = 202
    mock_refresh_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=[mock_token_response, mock_refresh_response]):
        result = await client.trigger_refresh()

    assert result is True
    assert client._token == "tok_new"
