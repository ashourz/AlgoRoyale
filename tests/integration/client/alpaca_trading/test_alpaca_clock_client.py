# src: tests/integration/client/test_alpaca_portfolio_client.py

from algo_royale import di
from algo_royale.di.container import DIContainer
from algo_royale.models.alpaca_trading.alpaca_clock import Clock
from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import AlpacaClockClient
import pytest
from algo_royale.di.container import di_container
from algo_royale.logging.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton.get_instance(LoggerType.TRADING, Environment.TEST)


@pytest.fixture
async def alpaca_client():
    client = di_container.alpaca_clock_client()
    yield client
    await client.aclose()  # Clean up the async client
    
@pytest.mark.asyncio
class TestAlpacaClockClientIntegration:

    async def test_fetch_clock(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = await alpaca_client.fetch_clock()

        assert result is not None
        assert isinstance(result, Clock)

        expected_attrs = [ "timestamp", "is_open", "next_open", "next_close" ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"