## db\dao\stock_data_dao.py
from datetime import datetime
from decimal import Decimal as Decimal
from typing import Optional, Tuple

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.logger_singleton import LoggerSingleton


class StockDataDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: LoggerSingleton,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_all_stock_data(
        self,
    ) -> list[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]:
        """Fetch all stock data."""
        return self.fetch("get_all_stock_data.sql", [])

    def fetch_stock_data_by_symbol(
        self, symbol: str
    ) -> list[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]:
        """Fetch stock data by symbol."""
        return self.fetch("get_stock_data_by_symbol.sql", (symbol,))

    def fetch_stock_data_by_symbol_and_date(
        self, symbol: str, start_time: datetime, end_time: datetime
    ) -> list[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]:
        """Fetch stock data by symbol and timestamp."""
        return self.fetch(
            "get_stock_data_by_symbol_and_date.sql", (symbol, start_time, end_time)
        )

    def fetch_latest_stock_data(
        self, symbol: str
    ) -> Optional[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]:
        """Fetch the latest stock data for a symbol."""
        return self.fetch_one("get_latest_stock_data.sql", (symbol,))

    def insert_stock_data(
        self,
        symbol: str,
        timestamp: datetime,
        open: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: int,
    ) -> None:
        """Insert new stock data."""
        return self.insert(
            "insert_stock_data.sql", (symbol, timestamp, open, high, low, close, volume)
        )

    def update_stock_data(
        self,
        stock_data_id: int,
        symbol: str,
        timestamp: datetime,
        open: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: int,
    ) -> None:
        """Update existing stock data."""
        return self.update(
            "update_stock_data.sql",
            (symbol, timestamp, open, high, low, close, volume, stock_data_id),
        )

    def delete_stock_data(self, stock_data_id: int) -> None:
        """Delete stock data by ID."""
        return self.delete("delete_stock_data.sql", (stock_data_id,))
