import pytest
from unittest.mock import AsyncMock, patch
from custom_components.miwifi_cb0401v2.api import MiWiFiClient

@pytest.fixture
def client():
    session = AsyncMock()
    return MiWiFiClient("192.168.31.1", "admin", "password", session)

@pytest.mark.asyncio
async def test_login(client):
    with patch("custom_components.miwifi_cb0401v2.api.aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value={"token": "test_token"})
        success = await client.login()
        assert success
        assert client._token == "test_token"

@pytest.mark.asyncio
async def test_fetch_mac_address(client):
    client._token = "test_token"
    with patch("custom_components.miwifi_cb0401v2.api.aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"hardware": {"mac": "00:11:22:33:44:55"}})
        mac_address = await client.fetch_mac_address()
        assert mac_address == "00:11:22:33:44:55"
