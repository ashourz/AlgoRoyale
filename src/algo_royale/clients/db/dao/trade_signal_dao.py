## db\dao\trade_signals_dao.py
from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable


##TODO: update to match updated schema
class TradeSignalDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: Loggable,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_all_signals(self) -> list[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch all trade signals."""
        return self.fetch("get_all_signals.sql", [])

    def fetch_signal_by_id(
        self, signal_id: int
    ) -> Optional[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch a trade signal by its ID."""
        return self.fetch("get_signal_by_id.sql", (signal_id,))

    def fetch_signals_by_symbol(
        self, symbol: str
    ) -> list[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch trade signals by symbol."""
        return self.fetch("get_signals_by_symbol.sql", (symbol,))

    def fetch_signals_by_symbol_and_date(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch trade signals by symbol and date."""
        return self.fetch(
            "get_signals_by_symbol_and_date.sql", (symbol, start_date, end_date)
        )

    def insert_signal(
        self, symbol: str, signal: str, price: Decimal, created_at: datetime
    ) -> None:
        """Insert a new trade signal."""
        return self.insert("insert_signal.sql", (symbol, signal, price, created_at))

    def update_signal(
        self,
        signal_id: int,
        symbol: str,
        signal: str,
        price: Decimal,
        created_at: datetime,
    ) -> None:
        """Update an existing trade signal."""
        return self.update(
            "update_signal.sql", (symbol, signal, price, created_at, signal_id)
        )

    def delete_signal(self, signal_id: int) -> None:
        """Delete a trade signal by its ID."""
        return self.delete("delete_signal.sql", (signal_id,))
