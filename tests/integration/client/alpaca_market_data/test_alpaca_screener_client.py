# src: tests/integration/client/test_alpaca_screener_client.py


import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    ActiveStockFilter,
    AlpacaScreenerClient,
)
from algo_royale.models.alpaca_market_data.alpaca_active_stock import (
    MostActiveStocksResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_market_mover import (
    MarketMoversResponse,
)
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
async def alpaca_client(monkeypatch):
    from unittest.mock import AsyncMock

    client = AlpacaScreenerClient(
        logger=logger,
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    # Patch the get method to return a fake response
    fake_response = {
        "market_type": "gainers",
        "most_actives": [
            {"symbol": "AAPL", "trade_count": 100, "volume": 10000},
            {"symbol": "GOOG", "trade_count": 80, "volume": 8000},
        ],
        "gainers": [
            {"symbol": "AAPL", "change": 5.0, "percent_change": 2.5, "price": 150.0}
        ],
        "losers": [
            {"symbol": "GOOG", "change": -3.0, "percent_change": -1.5, "price": 120.0}
        ],
        "next_page_token": None,
        "last_updated": "2024-09-14T12:00:00Z",
    }
    monkeypatch.setattr(client, "get", AsyncMock(return_value=fake_response))
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaScreenerClient:
    async def test_fetch_active_stocks(self, alpaca_client):
        """Test fetching active stocks data from Alpaca using a mock response."""
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
        """Test fetching market movers data from Alpaca using a mock response."""
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
