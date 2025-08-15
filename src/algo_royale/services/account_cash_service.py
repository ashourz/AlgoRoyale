from decimal import Decimal

from algo_royale.adapters.account_cash_adapter import AccountCashAdapter
from algo_royale.logging.loggable import Loggable


class AccountCashService:
    def __init__(self, cash_repo: AccountCashAdapter, logger: Loggable):
        self.cash_repo = cash_repo
        self.logger = logger
        self.buying_power: Decimal = self._fetch_buying_power()
        self.total_cash: Decimal = self._fetch_total_cash()

    def total_cash(self) -> Decimal:
        """Get the current total cash in the account."""
        return self.total_cash

    def buying_power(self) -> Decimal:
        """Get the current buying power of the account."""
        return self.buying_power

    def unsettled_cash(self) -> Decimal:
        """Get the current unsettled cash in the account."""
        return self.total_cash - self.buying_power

    async def async_update_cash_info(self) -> None:
        """Update the cash information by fetching the latest data from Alpaca."""
        try:
            self.buying_power = await self.cash_repo.fetch_buying_power()
            self.total_cash = await self.cash_repo.fetch_total_cash()
        except Exception as e:
            self.logger.error(f"Error updating cash info: {e}")
            pass
