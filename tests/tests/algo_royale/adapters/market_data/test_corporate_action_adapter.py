from datetime import datetime, timedelta, timezone

import pytest

from tests.mocks.adapters.mock_corporate_action_adapter import (
    MockCorporateActionAdapter,
)
from tests.mocks.clients.alpaca.mock_alpaca_corporate_action_client import (
    MockAlpacaCorporateActionClient,
)


@pytest.fixture
async def corporate_action_client():
    client = MockAlpacaCorporateActionClient()
    yield client
    await client.aclose()


@pytest.fixture
async def corporate_action_adapter(corporate_action_client):
    adapter = MockCorporateActionAdapter()
    yield adapter
    # No need to close the adapter, only the client


@pytest.mark.asyncio
class TestCorporateActionAdapter:
    async def test_get_corporate_actions_for_symbols(self, corporate_action_adapter):
        """Test for getting corporate actions."""
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        actions_response = (
            await corporate_action_adapter.get_corporate_actions_for_symbols(
                symbols=["AAPL"],
                start_date=start_date,
                end_date=end_date,
            )
        )
        assert actions_response is not None
        assert hasattr(actions_response, "corporate_actions")
        assert isinstance(actions_response.corporate_actions, dict)

    async def test_get_corporate_actions_by_ids(self, corporate_action_adapter):
        """Test for getting corporate actions by IDs."""
        action_ids = [1, 2, 3]
        actions_response = await corporate_action_adapter.get_corporate_actions_by_ids(
            action_ids
        )
        assert actions_response is not None
        assert hasattr(actions_response, "corporate_actions")
        assert isinstance(actions_response.corporate_actions, dict)

    async def test_get_corporate_actions_by_ids_no_results(
        self, corporate_action_adapter
    ):
        """Test for getting corporate actions by IDs with no results."""
        corporate_action_adapter.set_return_empty(True)
        actions_response = await corporate_action_adapter.get_corporate_actions_by_ids(
            action_ids=[9999]
        )
        assert actions_response is not None
        assert hasattr(actions_response, "corporate_actions")
        # Should be empty dict if no results
        assert len(actions_response.corporate_actions) == 0
        corporate_action_adapter.reset_return_empty()
