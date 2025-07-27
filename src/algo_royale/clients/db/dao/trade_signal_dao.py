## db\dao\trade_signals_dao.py
from datetime import datetime
from decimal import Decimal

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable


class TradeSignalDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: Loggable,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_all_signals(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all trade signals.
        Returns a list of all trade signals, limited by the specified limit and offset.
        parameters:
            limit (int): Maximum number of signals to return.
            offset (int): Number of signals to skip before starting to return results.
        """
        return self.fetch("get_all_signals.sql", (limit, offset))

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
        return self.fetch("get_signals_by_symbol.sql", (symbol, limit, offset))

    def upsert_signal(
        self,
        symbol: str,
        signal: str,
        price: Decimal,
        created_at: datetime,
        user_id: str = None,
        account_id: str = None,
    ) -> int:
        """Insert a new trade signal."""
        return self.insert(
            "upsert_signal.sql",
            (symbol, signal, price, created_at, user_id, account_id),
        )

    def delete_all_signals(self) -> int:
        """Delete all trade signals."""
        deleted_ids = self.delete("delete_all_signals.sql")
        return len(deleted_ids) if deleted_ids else 0
