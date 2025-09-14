# src: tests/integration/client/test_alpaca_portfolio_client.py


import pytest

from algo_royale.models.alpaca_trading.alpaca_clock import Clock
from tests.mocks.clients.mock_alpaca_clock_client import MockAlpacaClockClient
from tests.mocks.mock_loggable import MockLoggable


# Async fixture for MockAlpacaAccountClient
@pytest.fixture
async def alpaca_client():
    client = MockAlpacaClockClient(logger=MockLoggable())
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaClockClientIntegration:
    async def test_fetch_clock(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = await alpaca_client.fetch_clock()

        assert result is not None
        assert isinstance(result, Clock)

        expected_attrs = ["timestamp", "is_open", "next_open", "next_close"]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"
