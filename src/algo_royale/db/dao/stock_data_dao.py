## db\dao\stock_data_dao.py
import decimal
import datetime 
from algo_royale.db.dao.base_dao import BaseDAO
from algo_royale.db.db import connect_db

class StockDataDAO(BaseDAO):
    def __init__(self):
        pass  # No need to keep a connection open permanently

    def get_stock_data_by_symbol(self, symbol: str):
        """Get stock data for a specific stock symbol."""
        try:
            query = self._read_sql_file('get_stock_data_by_symbol.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise  
            # Re-raise the exception to be handled higher up in the call stack
    
    def insert_stock_data(self, symbol: str, timestamp: datetime, open: decimal, 
                          high: decimal, low: decimal, close: decimal, volume: int):
        """Insert new stock data into the database."""
        try:
            query = self._read_sql_file('insert_stock_data.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol, timestamp, open, high, low, close, volume))
                    conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error inserting stock data: {e}")
            # Log the error or re-raise it as needed
            raise
            # Re-raise the exception to be handled higher up in the call stack