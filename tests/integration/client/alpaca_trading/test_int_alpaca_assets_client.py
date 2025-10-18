import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import (
    AlpacaAssetsClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.utils.application_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_asset import Asset


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_assets_client
    try:
        yield client
    finally:
        await client_container.async_close_all_clients()


@pytest.mark.asyncio
class TestAlpacaAssetsClientIntegration:
    async def test_get_assets(self, alpaca_client: AlpacaAssetsClient):
        response = await alpaca_client.fetch_assets()
        assert response is not None
        assert isinstance(response, list)
        if response:
            assert isinstance(response[0], Asset)

    async def test_get_asset_by_symbol(self, alpaca_client: AlpacaAssetsClient):
        response = await alpaca_client.fetch_asset_by_symbol_or_id(
            symbol_or_asset_id="AAPL"
        )
        assert response is None or isinstance(response, Asset)
