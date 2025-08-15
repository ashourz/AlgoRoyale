from decimal import Decimal
from logging import Logger

from algo_royale.adapters.trading.account_adapter import AccountAdapter


class AccountCashAdapter:
    """Repository class to manage cash-related operations using AlpacaAccountService."""

    def __init__(self, account_adapter: AccountAdapter, logger: Logger):
        self.account_adapter = account_adapter

    async def fetch_buying_power(self) -> Decimal:
        """Fetch the current account buying power."""
        account = await self.account_adapter.get_account_data()
        if account and hasattr(account, "regt_buying_power"):
            self.logger.info(f"Current buying power: {account.regt_buying_power}")
            return Decimal(account.regt_buying_power)
        else:
            self.logger.error("Failed to fetch buying power from account data.")
        return Decimal(0)

    async def fetch_total_cash(self) -> Decimal:
        """Fetch the current cash balance in the account."""
        account = await self.account_adapter.get_account_data()
        if account and hasattr(account, "cash"):
            self.logger.info(f"Current total cash: {account.cash}")
            return Decimal(account.cash)
        else:
            self.logger.error("Failed to fetch total cash from account data.")
        return Decimal(0)
