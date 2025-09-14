from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_trading.alpaca_accounts_client import (
    AlpacaAccountClient,
)
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
from tests.mocks.mock_loggable import MockLoggable


# Async fixture for AlpacaAccountClient
@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaAccountClient(
        logger=MockLoggable(),
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    # Patch network methods to return fake responses
    monkeypatch.setattr(
        client,
        "fetch_account",
        AsyncMock(
            return_value=Account(
                id="id",
                account_number="123",
                status="ACTIVE",
                crypto_status="ACTIVE",
                currency="USD",
                cash="1000.0",
                portfolio_value="1000.0",
                non_marginable_buying_power="1000.0",
                accrued_fees="0.0",
                pending_transfer_in="",
                pending_transfer_out="",
                pattern_day_trader=False,
                trade_suspended_by_user=False,
                trading_blocked=False,
                transfers_blocked=False,
                account_blocked=False,
                created_at="2022-01-01T00:00:00Z",
                shorting_enabled=True,
                long_market_value="0.0",
                short_market_value="0.0",
                equity="1000.0",
                last_equity="1000.0",
                multiplier="1",
                buying_power="1000.0",
                initial_margin="0.0",
                maintenance_margin="0.0",
                sma="0.0",
                daytrade_count=0,
                last_maintenance_margin="0.0",
                daytrading_buying_power="1000.0",
                regt_buying_power="1000.0",
            )
        ),
    )
    monkeypatch.setattr(
        client,
        "fetch_account_configuration",
        AsyncMock(
            return_value=AccountConfiguration(
                dtbp_check=DTBPCheck.ENTRY,
                trade_confirm_email=TradeConfirmationEmail.NONE,
            )
        ),
    )
    monkeypatch.setattr(
        client,
        "update_account_configuration",
        AsyncMock(
            return_value=AccountConfiguration(
                dtbp_check=DTBPCheck.ENTRY,
                trade_confirm_email=TradeConfirmationEmail.NONE,
            )
        ),
    )
    from algo_royale.models.alpaca_trading.alpaca_account import AccountActivities

    monkeypatch.setattr(
        client,
        "get_account_activities",
        AsyncMock(return_value=AccountActivities(activities=[])),
    )
    monkeypatch.setattr(
        client,
        "get_account_activities_by_activity_type",
        AsyncMock(return_value=AccountActivities(activities=[])),
    )
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
