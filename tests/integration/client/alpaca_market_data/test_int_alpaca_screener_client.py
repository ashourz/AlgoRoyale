# src: tests/integration/client/alpaca_market_data/test_alpaca_screener_client.py
import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    AlpacaScreenerClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_market_data.alpaca_active_stock import (
    MostActiveStocksResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_market_mover import (
    MarketMoversResponse,
)
from algo_royale.models.alpaca_market_data.enums import ActiveStockFilter


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_screener_client
    try:
        yield client
    finally:
        client_container.close_all_clients()


@pytest.mark.asyncio
class TestAlpacaScreenerClientIntegration:
    async def test_fetch_active_stocks(self, alpaca_client: AlpacaScreenerClient):
        result = await alpaca_client.fetch_active_stocks(
            by=ActiveStockFilter.TRADES,
        )
        assert result is None or isinstance(result, MostActiveStocksResponse)

    async def test_fetch_market_movers(self, alpaca_client: AlpacaScreenerClient):
        result = await alpaca_client.fetch_market_movers()
        assert result is None or isinstance(result, MarketMoversResponse)
