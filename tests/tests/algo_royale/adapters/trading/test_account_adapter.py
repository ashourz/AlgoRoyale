import pytest

from tests.mocks.adapters.mock_account_adapter import MockAccountAdapter


@pytest.fixture
def account_adapter():
    adapter = MockAccountAdapter()
    yield adapter


@pytest.mark.asyncio
class TestAccountAdapter:
    async def test_get_account(self, account_adapter):
        result = await account_adapter.get_account()
        assert result is not None
        assert hasattr(result, "id")

    async def test_get_account_empty(self, account_adapter):
        account_adapter.set_return_empty(True)
        result = await account_adapter.get_account()
        assert result is None or result == {}
        account_adapter.reset_return_empty()
        # Use a valid ActivityType if available, else mock
        from algo_royale.models.alpaca_trading.enums.enums import ActivityType

        result = await account_adapter.get_account_activities_by_activity_type(
            ActivityType.FILL
        )
        assert result is not None
        assert hasattr(result, "activities")

    async def test_get_account_activities_by_activity_type_empty(self, account_adapter):
        from algo_royale.models.alpaca_trading.enums.enums import ActivityType

        account_adapter.set_return_empty(True)
        result = await account_adapter.get_account_activities_by_activity_type(
            ActivityType.FILL
        )
        assert result is not None
        assert result.activities == []
        account_adapter.reset_return_empty()
