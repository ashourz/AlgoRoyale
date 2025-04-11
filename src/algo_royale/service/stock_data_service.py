## service\stock_data_service.py
from decimal import Decimal
from datetime import datetime

from src.algo_royale.db.dao.stock_data_dao import StockDataDAO

class StockDataService:
    def __init__(self):
        self.stock_data_dao = StockDataDAO()

    def create_stock_data(self, symbol: str, timestamp: datetime, open_price: Decimal, high: Decimal, 
                          low: Decimal, close: Decimal, volume: int) -> None:
        """Insert stock data for a specific symbol."""
        self.stock_data_dao.insert_stock_data(symbol, timestamp, open_price, high, low, close, volume)

    def get_stock_data_by_symbol(self, symbol: str):
        """Fetch stock data for a specific symbol."""
        return self.stock_data_dao.fetch_stock_data_by_symbol(symbol)

    def get_latest_stock_data(self, symbol: str):
        """Fetch the latest stock data for a specific symbol."""
        return self.stock_data_dao.fetch_latest_stock_data(symbol)
