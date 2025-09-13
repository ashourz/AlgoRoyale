# src: tests/integration/client/test_alpaca_corporate_action_client.py

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateAction,
    CorporateActionResponse,
)
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
async def alpaca_client(monkeypatch):
    # Provide dummy config values
    client = AlpacaCorporateActionClient(
        logger=logger,
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    # Patch the get method to return a fake response
    fake_response = {
        "corporate_actions": {
            "AAPL": [
                {
                    "ex_date": "2024-04-01T00:00:00Z",
                    "foreign": False,
                    "payable_date": "2024-04-15T00:00:00Z",
                    "process_date": "2024-04-16T00:00:00Z",
                    "rate": 0.5,
                    "record_date": "2024-03-31T00:00:00Z",
                    "special": False,
                    "symbol": "AAPL",
                }
            ]
        },
        "next_page_token": None,
    }
    monkeypatch.setattr(client, "get", AsyncMock(return_value=fake_response))
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
