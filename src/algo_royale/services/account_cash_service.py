from decimal import Decimal

from algo_royale.adapters.account_cash_adapter import AccountCashAdapter
from algo_royale.logging.loggable import Loggable


class AccountCashService:
    def __init__(self, cash_adapter: AccountCashAdapter, logger: Loggable):
        self.cash_adapter = cash_adapter
        self.logger = logger
        self.buying_power: Decimal = 0
        self.total_cash: Decimal = 0

    def total_cash(self) -> Decimal:
        """Get the current total cash in the account."""
        return self.total_cash

    def buying_power(self) -> Decimal:
        """Get the current buying power of the account."""
        return self.buying_power

    def unsettled_cash(self) -> Decimal:
        """Get the current unsettled cash in the account."""
        return self.total_cash - self.buying_power

    async def async_update_cash_info(self):
        """Update the cash information by fetching the latest data from Alpaca."""
        try:
            account_data = await self.cash_adapter.fetch_account_data()
            if account_data:
                self.buying_power = Decimal(account_data.regt_buying_power)
                self.total_cash = Decimal(account_data.cash)
        except Exception as e:
            self.logger.error(f"Error updating cash info: {e}")
            self.buying_power = Decimal(0)
            self.total_cash = Decimal(0)
