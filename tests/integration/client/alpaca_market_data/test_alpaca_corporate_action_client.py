from datetime import datetime, timezone

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
    CorporateActionResponse,
)


@pytest.fixture
async def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    adapter = application.adapter_container
    client_container = adapter.client_container
    client = client_container.alpaca_corporate_action_client
    try:
        yield client
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close"):
            client.close()


@pytest.mark.asyncio
class TestAlpacaCorporateActionClientIntegration:
    async def test_get_corporate_actions(
        self, alpaca_client: AlpacaCorporateActionClient
    ):
        # Replace with a real method and parameters for your client
        # For example, get corporate actions for a known symbol/date
        response = await alpaca_client.fetch_corporate_actions(
            symbols=["AAPL"],
            start_date=datetime(2024, 4, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 4, 3, tzinfo=timezone.utc),
        )
        assert response is not None
        assert isinstance(response, CorporateActionResponse)
        # Optionally, check for expected keys/fields in the response
        if response:
            assert response.corporate_actions is not None
