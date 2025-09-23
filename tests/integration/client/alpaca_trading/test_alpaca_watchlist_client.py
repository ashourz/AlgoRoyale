import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_trading.alpaca_watchlist import Watchlist


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_watchlist_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaWatchlistClientIntegration:
    async def test_get_watchlists(self, alpaca_client: AlpacaWatchlistClient):
        response = await alpaca_client.get_watchlists()
        assert response is not None
        assert isinstance(response, list)
        if response:
            assert isinstance(response[0], Watchlist)

    async def test_get_watchlist_by_id(self, alpaca_client: AlpacaWatchlistClient):
        # Replace 'watchlist_id' with a valid watchlist id for a real test
        watchlist_id = "test_watchlist_id"
        response = await alpaca_client.get_watchlist_by_id(watchlist_id)
        assert response is None or isinstance(response, Watchlist)
