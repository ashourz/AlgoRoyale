## service\trade_signal_service.py
from datetime import datetime
from decimal import Decimal

from algo_royale.clients.db.dao.trade_signal_dao import TradeSignalDAO
from algo_royale.logging.loggable import Loggable


class TradeSignalService:
    def __init__(
        self, dao: TradeSignalDAO, logger: Loggable, user_id: str, account_id: str
    ):
        self.dao = dao
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    def fetch_all_signals(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all trade signals.
        Returns a list of all trade signals, limited by the specified limit and offset.
        parameters:
            limit (int): Maximum number of signals to return.
            offset (int): Number of signals to skip before starting to return results.
        """
        return self.dao.fetch_all_signals(limit, offset)

    def fetch_signals_by_symbol(
        self, symbol: str, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch trade signals by symbol.
        Returns a list of signals for the given symbol, limited by the specified limit and offset.
        parameters:
            symbol (str): The stock symbol to filter signals by.
            limit (int): Maximum number of signals to return.
            offset (int): Number of signals to skip before starting to return results.
        """
        return self.dao.fetch_signals_by_symbol(symbol, limit, offset)

    def upsert_signal(
        self,
        symbol: str,
        signal: str,
        price: Decimal,
        created_at: datetime,
    ) -> int:
        """Insert or update a trade signal."""
        return self.dao.upsert_signal(
            symbol, signal, price, created_at, self.user_id, self.account_id
        )

    def delete_all_signals(self) -> int:
        """Delete all trade signals.
        Returns the number of deleted signals.
        """
        return self.dao.delete_all_signals()
