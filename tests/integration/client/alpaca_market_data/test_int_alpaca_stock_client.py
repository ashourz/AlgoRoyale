# src: tests/integration/client/alpaca_market_data/test_alpaca_stock_client.py
from datetime import datetime, timezone

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stock_client import (
    AlpacaStockClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_market_data.alpaca_auction import AuctionResponse
from algo_royale.models.alpaca_market_data.alpaca_bar import (
    BarsResponse,
    LatestBarsResponse,
)
from algo_royale.models.alpaca_market_data.alpaca_quote import QuotesResponse


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_stock_client
    try:
        yield client
    finally:
        client_container.close_all_clients()


@pytest.mark.asyncio
class TestAlpacaStockClientIntegration:
    async def test_fetch_historical_quotes(self, alpaca_client: AlpacaStockClient):
        result = await alpaca_client.fetch_historical_quotes(
            symbols=["AAPL"],
            start_date=datetime(2024, 4, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 4, 3, tzinfo=timezone.utc),
        )
        assert result is None or isinstance(result, QuotesResponse)

    async def test_fetch_latest_quotes(self, alpaca_client: AlpacaStockClient):
        result = await alpaca_client.fetch_latest_quotes(symbols=["AAPL"])
        assert result is None or isinstance(result, QuotesResponse)

    async def test_fetch_historical_auctions(self, alpaca_client: AlpacaStockClient):
        result = await alpaca_client.fetch_historical_auctions(
            symbols=["AAPL"],
            start_date=datetime(2024, 4, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 4, 3, tzinfo=timezone.utc),
        )
        assert result is None or isinstance(result, AuctionResponse)

    async def test_fetch_historical_bars(self, alpaca_client: AlpacaStockClient):
        result = await alpaca_client.fetch_historical_bars(
            symbols=["AAPL"],
            start_date=datetime(2024, 4, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 4, 3, tzinfo=timezone.utc),
        )
        assert result is None or isinstance(result, BarsResponse)

    async def test_fetch_latest_bars(self, alpaca_client: AlpacaStockClient):
        result = await alpaca_client.fetch_latest_bars(symbols=["AAPL"])
        assert result is None or isinstance(result, LatestBarsResponse)
