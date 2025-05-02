# src: tests/integration/client/test_alpaca_account_client.py

from datetime import datetime, timedelta
import pytest
from algo_royale.shared.models.alpaca_trading.alpaca_account import Account, AccountActivities, AccountConfiguration
from algo_royale.shared.models.alpaca_trading.enums import ActivityType, DTBPCheck, TradeConfirmationEmail
from algo_royale.the_risk_is_not_enough.client.alpaca_trading.alpaca_accounts_client import AlpacaAccountClient

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()


@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaAccountClient()

@pytest.mark.asyncio
class TestAlpacaAccountClientIntegration:

    def test_fetch_account(self, alpaca_client):
        """Test fetching account data from Alpaca's live endpoint."""

        result = alpaca_client.fetch_account()

        assert result is not None
        assert isinstance(result, Account)

        expected_attrs = [
            "id", "account_number", "status", "crypto_status", "currency",
            "cash", "portfolio_value", "non_marginable_buying_power", "accrued_fees",
            "pending_transfer_in", "pending_transfer_out", "pattern_day_trader",
            "trade_suspended_by_user", "trading_blocked", "transfers_blocked",
            "account_blocked", "created_at", "shorting_enabled", "long_market_value",
            "short_market_value", "equity", "last_equity", "multiplier",
            "buying_power", "initial_margin", "maintenance_margin", "sma",
            "daytrade_count", "last_maintenance_margin", "daytrading_buying_power",
            "regt_buying_power"
        ]

        for attr in expected_attrs:
            assert hasattr(result, attr), f"Missing expected attribute: {attr}"
            assert getattr(result, attr) is not None, f"{attr} is None"    
            
    def test_fetch_account_configuration(self, alpaca_client):
        """Test retrieving account configuration settings."""
        config = alpaca_client.fetch_account_configuration()
        assert config is not None
        assert isinstance(config, AccountConfiguration)
        assert hasattr(config, "dtbp_check")

    def test_update_account_configuration(self, alpaca_client):
        """Test updating account configuration settings."""
        updated = alpaca_client.update_account_configuration(
            suspend_trade=False,
            no_shorting=False,
            fractional_trading=True,
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE
        )
        assert updated is not None
        assert isinstance(updated, AccountConfiguration)
        assert updated.dtbp_check == DTBPCheck.ENTRY
        assert updated.trade_confirm_email == TradeConfirmationEmail.NONE

    def test_get_account_activities(self, alpaca_client):
        """Test fetching general account activities."""
        activities = alpaca_client.get_account_activities(
            after=datetime.now() - timedelta(days=30),
            page_size=5
        )
        assert activities is not None
        assert isinstance(activities, AccountActivities)

    def test_get_account_activities_by_type(self, alpaca_client):
        """Test fetching account activities by specific activity type."""
        activity_type = ActivityType.FILL
        activities = alpaca_client.get_account_activities_by_activity_type(
            activity_type=activity_type
        )
        assert activities is not None
        assert isinstance(activities, AccountActivities)