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


class MockAlpacaAccountClient(AlpacaAccountClient):
    def __init__(self):
        self.logger = MockLoggable()
        self.return_empty = False
        self.throw_exception = False
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )

    async def fetch_account(self):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAccountClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
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
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAccountClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return AccountConfiguration(
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE,
        )

    async def update_account_configuration(self, **kwargs):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAccountClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return AccountConfiguration(
            dtbp_check=DTBPCheck.ENTRY,
            trade_confirm_email=TradeConfirmationEmail.NONE,
        )

    async def get_account_activities(
        self,
        activity_types=None,
        category=None,
        date=None,
        until=None,
        after=None,
        direction=None,
        page_size=None,
        page_token=None,
    ):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAccountClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return AccountActivities(activities=[])
        return AccountActivities(activities=[])

    async def get_account_activities_by_activity_type(
        self,
        activity_type: ActivityType,
        date=None,
        until=None,
        after=None,
        direction=None,
        page_size=None,
        page_token=None,
    ):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaAccountClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return AccountActivities(activities=[])
        return AccountActivities(activities=[])

    async def aclose(self):
        pass
