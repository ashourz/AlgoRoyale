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


class MockAlpacaAccountClient:
    def __init__(self):
        self.logger = MockLoggable()

    async def fetch_account(self):
        return Account(
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

    async def fetch_account_configuration(self):
        return AccountConfiguration(
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE,
        )

    async def update_account_configuration(self, **kwargs):
        return AccountConfiguration(
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE,
        )

    async def get_account_activities(self, after=None, page_size=None):
        return AccountActivities(activities=[])

    async def get_account_activities_by_activity_type(
        self, activity_type: ActivityType
    ):
        return AccountActivities(activities=[])

    async def aclose(self):
        pass
