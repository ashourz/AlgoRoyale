# src/algo_royale/db/dao/stock_data_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO

class StockDataDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_all_stock_data(self):
        return self.fetch("get_all_stock_data.sql", [])

    def fetch_stock_data_by_symbol(self, symbol: str):
        return self.fetch("get_stock_data_by_symbol.sql", (symbol,))

    def insert_stock_data(self, symbol: str, timestamp: datetime, open: decimal, high: decimal, low: decimal, close: decimal, volume: int):
        return self.insert(
            "insert_stock_data.sql",
            (symbol, timestamp, open, high, low, close, volume)
        )

    def update_stock_data(self, stock_data_id: int, symbol: str, timestamp: datetime, open: decimal, high: decimal, low: decimal, close: decimal, volume: int):
        return self.update(
            "update_stock_data.sql",
            (symbol, timestamp, open, high, low, close, volume, stock_data_id)
        )

    def delete_stock_data(self, stock_data_id: int):
        return self.delete("delete_stock_data.sql", (stock_data_id,))
