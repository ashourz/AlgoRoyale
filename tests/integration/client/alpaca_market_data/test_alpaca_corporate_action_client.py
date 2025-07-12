# src: tests/integration/client/test_alpaca_corporate_action_client.py

from datetime import datetime, timezone

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from algo_royale.di.container import DIContainer
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateAction,
    CorporateActionResponse,
)

# Set up logging (prints to console)
logger = LoggerFactory.get_base_logger(LoggerEnv.TEST)


@pytest.fixture
async def alpaca_client(event_loop):
    client = AlpacaCorporateActionClient(
        trading_config=DIContainer.trading_config(),
    )
    yield client
    await client.aclose()  # Clean up the async cli    ent


@pytest.mark.asyncio
class TestAlpacaCorporateActionClientIntegration:
    async def test_fetch_corporate_actions(self, alpaca_client):
        """Test fetching corporate actions data from Alpaca's live endpoint."""
        symbols = ["AAPL", "GOOGL"]
        start_date = datetime(2020, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = await alpaca_client.fetch_corporate_actions(
            symbols=symbols, start_date=start_date, end_date=end_date
        )

        logger.warning(f"result {result}")
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
