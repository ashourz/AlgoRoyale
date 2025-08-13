from decimal import Decimal
from logging import Logger

from algo_royale.services.trading.account_adapter import AccountAdapter


class AccountCashAdapter:
    """Repository class to manage cash-related operations using AlpacaAccountService."""

    def __init__(self, account_service: AccountAdapter, logger: Logger):
        self.account_service = account_service
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

    async def _fetch_buying_power(self) -> Decimal:
        """Fetch the current account buying power."""
        account = await self.account_service.get_account_data()
        if account and hasattr(account, "regt_buying_power"):
            self.logger.info(f"Current buying power: {account.regt_buying_power}")
            return Decimal(account.regt_buying_power)
        else:
            self.logger.error("Failed to fetch buying power from account data.")
        return Decimal(0)

    async def _fetch_total_cash(self) -> Decimal:
        """Fetch the current cash balance in the account."""
        account = await self.account_service.get_account_data()
        if account and hasattr(account, "cash"):
            self.logger.info(f"Current total cash: {account.cash}")
            return Decimal(account.cash)
        else:
            self.logger.error("Failed to fetch total cash from account data.")
        return Decimal(0)

    async def update_cash_info(self) -> None:
        """Update the cash information by fetching the latest data from Alpaca."""
        try:
            self.buying_power = await self._fetch_buying_power()
            self.total_cash = await self._fetch_total_cash()
        except Exception as e:
            self.logger.error(f"Error updating cash info: {e}")
            pass
