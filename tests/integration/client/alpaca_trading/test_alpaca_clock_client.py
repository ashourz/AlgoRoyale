# src: tests/integration/client/test_alpaca_portfolio_client.py

import logging
from algo_royale.client.alapaca_trading.alpaca_clock_client import AlpacaClockClient
from models.alpaca_trading.alpaca_clock import Clock
import pytest

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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