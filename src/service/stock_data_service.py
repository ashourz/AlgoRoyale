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

    def get_all_stock_data(self) -> list:
        """Fetch all stock data."""
        return self.stock_data_dao.fetch_all_stock_data()   
    
    def get_stock_data_by_symbol(self, symbol: str) -> list:
        """Fetch stock data for a specific symbol."""
        return self.stock_data_dao.fetch_stock_data_by_symbol(symbol)

    def get_stock_data_by_symbol_and_timestamp(self, symbol: str, start_time: datetime, end_time: datetime) -> list:
        """Fetch stock data for a specific symbol within a time range."""
        return self.stock_data_dao.fetch_stock_data_by_symbol_and_timestamp(symbol, start_time, end_time)   
    
    def update_stock_data(self, stock_data_id: int, symbol: str, timestamp: datetime, open_price: Decimal, high: Decimal, 
                        low: Decimal, close: Decimal, volume: int) -> None:
        """Update existing stock data."""
        self.stock_data_dao.update_stock_data(stock_data_id, symbol, timestamp, open_price, high, low, close, volume)   
        
    def delete_stock_data(self, stock_data_id: int) -> None:
        """Delete stock data by ID."""
        self.stock_data_dao.delete_stock_data(stock_data_id)    
        
    def get_latest_stock_data(self, symbol: str) -> tuple:
        """Fetch the latest stock data for a symbol."""
        return self.stock_data_dao.fetch_latest_stock_data(symbol)  
    