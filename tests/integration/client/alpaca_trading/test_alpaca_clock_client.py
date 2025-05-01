# src: tests/integration/client/test_alpaca_portfolio_client.py

from shared.models.alpaca_trading.alpaca_clock import Clock
from the_risk_is_not_enough.client.alpaca_trading.alpaca_clock_client import AlpacaClockClient
import pytest

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaClockClient()

@pytest.mark.asyncio
class TestAlpacaClockClientIntegration:

    def test_fetch_clock(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = alpaca_client.fetch_clock()

        assert result is not None
        assert isinstance(result, Clock)

        expected_attrs = [ "timestamp", "is_open", "next_open", "next_close" ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"