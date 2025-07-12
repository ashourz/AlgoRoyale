# src: tests/integration/client/test_alpaca_screener_client.py

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    ActiveStockFilter,
    AlpacaScreenerClient,
)
from algo_royale.di.container import DIContainer
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.models.alpaca_market_data.alpaca_active_stock import (
    MostActiveStocksResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_market_mover import (
    MarketMoversResponse,
)

# Set up logging (prints to console)
logger = LoggerFactory.get_base_logger(LoggerEnv.TEST)


@pytest.fixture
async def alpaca_client():
    client = AlpacaScreenerClient(trading_config=DIContainer.trading_config())
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaScreenerClientIntegration:
    async def test_fetch_active_stocks(self, alpaca_client):
        """Test fetching active stocks data from Alpaca's live endpoint."""
        by = ActiveStockFilter.VOLUME
        top = 10
        result = await alpaca_client.fetch_active_stocks(by=by, top=top)

        assert result is not None
        assert isinstance(result, MostActiveStocksResponse)
        assert len(result.most_actives) > 0
        first_stock = result.most_actives[0]

        expected_attrs = ["symbol", "trade_count", "volume"]
        for attr in expected_attrs:
            assert hasattr(first_stock, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_stock, attr) is not None, f"{attr} is None"

    async def test_fetch_market_movers(self, alpaca_client):
        """Test fetching market movers data from Alpaca's live endpoint."""
        top = 10
        result = await alpaca_client.fetch_market_movers(top=top)

        assert result is not None
        assert isinstance(result, MarketMoversResponse)
        assert len(result.gainers) > 0
        assert len(result.losers) > 0

        first_gainer = result.gainers[0]
        first_loser = result.losers[0]

        expected_attrs = ["symbol", "change", "percent_change", "price"]
        for attr in expected_attrs:
            assert hasattr(first_gainer, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_gainer, attr) is not None, f"{attr} is None"

            assert hasattr(first_loser, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_loser, attr) is not None, f"{attr} is None"
