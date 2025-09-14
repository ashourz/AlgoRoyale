# src: tests/integration/client/test_alpaca_corporate_action_client.py

from datetime import datetime, timezone

import pytest

from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateAction,
    CorporateActionResponse,
)
from tests.mocks.mock_alpaca_corporate_action_client import (
    MockAlpacaCorporateActionClient,
)
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
async def alpaca_client():
    client = MockAlpacaCorporateActionClient(logger=logger)
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaCorporateActionClient:
    async def test_fetch_corporate_actions(self, alpaca_client):
        """Test fetching corporate actions data from Alpaca using a mock response."""
        symbols = ["AAPL"]
        start_date = datetime(2020, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = await alpaca_client.fetch_corporate_actions(
            symbols=symbols, start_date=start_date, end_date=end_date
        )

        assert result is not None
        assert isinstance(result, CorporateActionResponse)
        assert len(result.corporate_actions) > 0

        first_action = next(iter(result.corporate_actions.values()))[0]
        assert isinstance(first_action, CorporateAction)

        expected_attrs = [
            "ex_date",
            "foreign",
            "payable_date",
            "process_date",
            "rate",
            "record_date",
            "special",
            "symbol",
        ]
        for attr in expected_attrs:
            assert hasattr(first_action, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_action, attr) is not None, f"{attr} is None"
