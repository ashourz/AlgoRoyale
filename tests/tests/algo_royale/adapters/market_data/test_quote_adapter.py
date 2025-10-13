import datetime

import pytest

from algo_royale.adapters.market_data.quote_adapter import QuoteAdapter
from algo_royale.models.alpaca_market_data.enums import Tape, TickType
from tests.mocks.clients.alpaca.mock_alpaca_stock_client import MockAlpacaStockClient
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def quote_adapter():
    adapter = QuoteAdapter(
        alpaca_stock_client=MockAlpacaStockClient(), logger=MockLoggable()
    )
    yield adapter


def set_adapter_return_empty(adapter: QuoteAdapter, value: bool):
    adapter.client.return_empty = value


def reset_adapter_return_empty(adapter: QuoteAdapter):
    adapter.client.return_empty = False


@pytest.mark.asyncio
class TestQuoteAdapter:
    async def test_fetch_historical_quotes(self, quote_adapter):
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_quotes(["AAPL"], start, end)
        assert result is not None

    async def test_fetch_latest_quotes(self, quote_adapter):
        result = await quote_adapter.fetch_latest_quotes(["AAPL"])
        assert result is not None

    async def test_fetch_historical_auctions(self, quote_adapter):
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_auctions(["AAPL"], start, end)
        assert result is not None

    async def test_fetch_historical_bars(self, quote_adapter):
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_bars(["AAPL"], start, end)
        assert result is not None

    async def test_fetch_latest_bars(self, quote_adapter):
        result = await quote_adapter.fetch_latest_bars(["AAPL"])
        assert result is not None

    async def test_fetch_condition_codes(self, quote_adapter):
        result = await quote_adapter.fetch_condition_codes(TickType.TRADE, Tape.A)
        assert result is not None

    async def test_fetch_snapshots(self, quote_adapter):
        result = await quote_adapter.fetch_snapshots(["AAPL"])
        assert result is not None

    async def test_fetch_historical_trades(self, quote_adapter):
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_trades(["AAPL"], start, end)
        assert result is not None

    async def test_fetch_latest_trades(self, quote_adapter):
        result = await quote_adapter.fetch_latest_trades(["AAPL"])
        assert result is not None

    async def test_fetch_historical_quotes_empty(self, quote_adapter):
        set_adapter_return_empty(quote_adapter, True)
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_quotes(["AAPL"], start, end)
        assert result is None
        reset_adapter_return_empty(quote_adapter)
