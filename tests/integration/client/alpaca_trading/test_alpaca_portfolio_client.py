# src: tests/integration/client/test_alpaca_portfolio_client.py

from datetime import datetime
from algo_royale.client.alpaca_trading.alpaca_portfolio_client import AlpacaPortfolioClient
from models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
import pytest

from logger.log_config import LoggerType, get_logger

# Set up logging (prints to console)
logger = get_logger(LoggerType.INTEGRATION)


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaPortfolioClient()

@pytest.mark.asyncio
class TestAlpacaPortfolioClientIntegration:

    def test_fetch_portfolio_history(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = alpaca_client.fetch_portfolio_history(
            period="1M", 
            timeframe= "1D"
            )

        assert result is not None
        assert isinstance(result, PortfolioPerformance)

        expected_attrs = [
            "timestamp", "equity", "profit_loss", "profit_loss_pct",
            "base_value", "timeframe", "base_value_asof"
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"
            assert isinstance(getattr(result, attr), list) or isinstance(getattr(result, attr), (float, str, datetime)), f"{attr} is not the expected type"