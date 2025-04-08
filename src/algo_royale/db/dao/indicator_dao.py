## db\dao\indicator_dao.py
import decimal
import datetime
from db.dao.base_dao import BaseDAO
from db.db import connect_db

class IndicatorDAO(BaseDAO):
    def __init__(self):
        pass # No need to keep a connection open permanently
    
    def get_indicators_by_trade_id(self, trade_id: int):
        """Get indicators for a specific stock symbol."""
        try:
            query = self._read_sql_file('get_indicators_by_trade_id.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (trade_id,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error fetching indicators: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise
            # Re-raise the exception to be handled higher up in the call stack

        
    def insert_indicator(self, trade_id: int, rsi: decimal, macd: decimal, volumr: decimal, 
                         bollinger_upper: decimal, bollinger_lower: decimal, atr: decimal, 
                         price: decimal, ema_short: decimal, ema_long: decimal, recorded_at: datetime):
        """Insert a new indicator into the database."""
        try:
            query = self._read_sql_file('insert_indicator.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (trade_id, rsi, macd, volumr, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at))
                    conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error inserting indicator: {e}")
            # Log the error or re-raise it as needed
            raise
            # Re-raise the exception to be handled higher up in the call stack
