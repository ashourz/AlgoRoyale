## db\dao\stock_data_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO
from decimal import Decimal as Decimal
from datetime import datetime
from typing import List, Optional, Tuple

class StockDataDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_all_stock_data(self) -> List[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]:
        """Fetch all stock data."""
        return self.fetch("get_all_stock_data.sql", [])

    def fetch_stock_data_by_symbol(self, symbol: str) -> List[Tuple[int, str, datetime, Decimal, Decimal, Decimal, Decimal, int]]: 
        """Fetch stock data by symbol."""
        return self.fetch("get_stock_data_by_symbol.sql", (symbol,))

    def insert_stock_data(self, symbol: str, timestamp: datetime, open: Decimal, high: Decimal, low: Decimal, close: Decimal, volume: int) -> None:
        """Insert new stock data."""
        return self.insert(
            "insert_stock_data.sql",
            (symbol, timestamp, open, high, low, close, volume)
        )

    def update_stock_data(self, stock_data_id: int, symbol: str, timestamp: datetime, open: Decimal, high: Decimal, low: Decimal, close: Decimal, volume: int) -> None:
        """Update existing stock data."""
        return self.update(
            "update_stock_data.sql",
            (symbol, timestamp, open, high, low, close, volume, stock_data_id)
        )

    def delete_stock_data(self, stock_data_id: int) -> None:
        """Delete stock data by ID."""
        return self.delete("delete_stock_data.sql", (stock_data_id,))