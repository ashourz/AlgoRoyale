from algo_royale.models.alpaca_trading.alpaca_account import Account


class MockAccountCashAdapter:
    def __init__(self):
        from datetime import datetime

        from algo_royale.models.alpaca_trading.alpaca_account import AccountStatus

        self.account_data = Account(
            id="mock_id",
            account_number="MOCK123456",
            status=AccountStatus.ACTIVE,
            crypto_status=AccountStatus.ACTIVE,
            currency="USD",
            cash="10000.00",
            portfolio_value="10000.00",
            non_marginable_buying_power="8000.00",
            accrued_fees="0.00",
            pending_transfer_in="0.00",
            pending_transfer_out="0.00",
            pattern_day_trader=False,
            trade_suspended_by_user=False,
            trading_blocked=False,
            transfers_blocked=False,
            account_blocked=False,
            created_at=datetime(2024, 1, 1),
            shorting_enabled=True,
            long_market_value="0.00",
            short_market_value="0.00",
            equity="10000.00",
            last_equity="10000.00",
            multiplier="2",
            buying_power="20000.00",
            initial_margin="0.00",
            maintenance_margin="0.00",
            sma="0.00",
            daytrade_count=0,
            last_maintenance_margin="0.00",
            daytrading_buying_power="18000.00",
            regt_buying_power="9000.00",
        )
        self._raise_exception = False

    async def fetch_account_data(self) -> Account | None:
        if self._raise_exception:
            raise Exception("Mocked account data fetch error")
        return self.account_data

    def set_raise_exception(self, value: bool):
        self._raise_exception = value

    def reset_raise_exception(self):
        self._raise_exception = False
