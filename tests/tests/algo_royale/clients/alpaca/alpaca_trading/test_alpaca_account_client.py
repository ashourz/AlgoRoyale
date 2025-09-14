from datetime import datetime, timedelta

import pytest

from algo_royale.models.alpaca_trading.alpaca_account import (
    Account,
    AccountActivities,
    AccountConfiguration,
)
from algo_royale.models.alpaca_trading.enums.enums import (
    ActivityType,
    DTBPCheck,
    TradeConfirmationEmail,
)
from tests.mocks.clients.mock_alpaca_account_client import MockAlpacaAccountClient


# Async fixture for MockAlpacaAccountClient
@pytest.fixture
async def alpaca_client():
    client = MockAlpacaAccountClient()
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaAccountClient:
    """Test class for AlpacaAccountClient with setup/teardown methods"""

    async def test_fetch_account(self, alpaca_client):
        result = await alpaca_client.fetch_account()
        assert result is not None
        assert isinstance(result, Account)

        expected_attrs = [
            "id",
            "account_number",
            "status",
            "crypto_status",
            "currency",
            "cash",
            "portfolio_value",
            "non_marginable_buying_power",
            "accrued_fees",
            "pending_transfer_in",
            "pending_transfer_out",
            "pattern_day_trader",
            "trade_suspended_by_user",
            "trading_blocked",
            "transfers_blocked",
            "account_blocked",
            "created_at",
            "shorting_enabled",
            "long_market_value",
            "short_market_value",
            "equity",
            "last_equity",
            "multiplier",
            "buying_power",
            "initial_margin",
            "maintenance_margin",
            "sma",
            "daytrade_count",
            "last_maintenance_margin",
            "daytrading_buying_power",
            "regt_buying_power",
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing attribute: {attr}"
            if attr not in [
                "pending_transfer_in",
                "pending_transfer_out",
                "accrued_fees",
            ]:
                assert getattr(result, attr) is not None, f"{attr} is None"

    async def test_fetch_account_configuration(self, alpaca_client):
        config = await alpaca_client.fetch_account_configuration()
        assert config is not None
        assert isinstance(config, AccountConfiguration)
        assert hasattr(config, "dtbp_check")

    async def test_update_account_configuration(self, alpaca_client):
        updated = await alpaca_client.update_account_configuration(
            suspend_trade=False,
            no_shorting=False,
            fractional_trading=True,
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE,
        )
        assert updated is not None
        assert isinstance(updated, AccountConfiguration)
        assert updated.dtbp_check == DTBPCheck.ENTRY
        assert updated.trade_confirm_email == TradeConfirmationEmail.NONE

    async def test_get_account_activities(self, alpaca_client):
        activities = await alpaca_client.get_account_activities(
            after=datetime.now() - timedelta(days=30), page_size=5
        )
        assert activities is not None
        assert isinstance(activities, AccountActivities)

    async def test_get_account_activities_by_type(self, alpaca_client):
        activity_type = ActivityType.FILL
        activities = await alpaca_client.get_account_activities_by_activity_type(
            activity_type=activity_type
        )
        assert activities is not None
        assert isinstance(activities, AccountActivities)
