from logging import Logger

from algo_royale.adapters.trading.account_adapter import AccountAdapter
from algo_royale.models.alpaca_trading.alpaca_account import Account


class AccountCashAdapter:
    """Repository class to manage cash-related operations using AlpacaAccountService."""

    def __init__(self, account_adapter: AccountAdapter, logger: Logger):
        self.account_adapter = account_adapter

    async def fetch_account_data(self) -> Account | None:
        """Fetch the account data from the Alpaca API."""
        try:
            return await self.account_adapter.get_account_data()
        except Exception as e:
            self.logger.error(f"Error fetching account data: {e}")
        return None
