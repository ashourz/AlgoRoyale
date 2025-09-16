import datetime

import pytest

from algo_royale.models.alpaca_market_data.enums import Tape, TickType
from tests.mocks.adapters.mock_quote_adapter import MockQuoteAdapter


@pytest.fixture
def quote_adapter():
    adapter = MockQuoteAdapter()
    yield adapter


@pytest.mark.asyncio
class TestQuoteAdapter:
    # Test all public async methods of QuoteAdapter
    import datetime

    from alpaca.common.enums import Sort, SupportedCurrencies
    from alpaca.data.enums import Adjustment, DataFeed
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

    from algo_royale.models.alpaca_market_data.enums import SnapshotFeed, Tape, TickType

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
        quote_adapter.set_return_empty(True)
        start = datetime.datetime(2024, 1, 1)
        end = datetime.datetime(2024, 1, 2)
        result = await quote_adapter.fetch_historical_quotes(["AAPL"], start, end)
        assert result is None
        quote_adapter.reset_return_empty()
