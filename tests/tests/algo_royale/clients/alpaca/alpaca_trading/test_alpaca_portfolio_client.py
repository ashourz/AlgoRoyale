# src: tests/integration/client/test_alpaca_portfolio_client.py


from datetime import datetime

import pytest

from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from tests.mocks.clients.mock_alpaca_portfolio_client import MockAlpacaPortfolioClient
from tests.mocks.mock_loggable import MockLoggable


# Async fixture for MockAlpacaAccountClient
@pytest.fixture
async def alpaca_client():
    client = MockAlpacaPortfolioClient(logger=MockLoggable())
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaPortfolioClientIntegration:
    async def test_fetch_portfolio_history(self, alpaca_client):
        """Test fetching portfolio history data from Alpaca's live endpoint."""

        result = await alpaca_client.fetch_portfolio_history(
            period="1M", timeframe="1D"
        )

        assert result is not None
        assert isinstance(result, PortfolioPerformance)

        expected_attrs = [
            "timestamp",
            "equity",
            "profit_loss",
            "profit_loss_pct",
            "base_value",
            "timeframe",
            "base_value_asof",
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"
            assert isinstance(getattr(result, attr), list) or isinstance(
                getattr(result, attr), (float, str, datetime)
            ), f"{attr} is not the expected type"
