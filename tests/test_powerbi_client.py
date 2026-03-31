import pytest
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


@pytest.mark.asyncio
async def test_trigger_refresh_calls_correct_endpoint():
    client = make_client()
    client._token = "tok_abc123"

    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        result = await client.trigger_refresh()

    assert result is True
    call_url = mock_post.call_args[0][0]
    assert "datasets/ds_456/refreshes" in call_url
