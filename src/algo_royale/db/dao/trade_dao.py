## db\dao\trade_dao.py

import decimal
import datetime
from db.dao.base_dao import BaseDAO

class TradeDAO(BaseDAO):
    def __init__(self):
        pass  # No need to keep a connection open permanently
    
    def get_recent_trades(self, symbol: str, limit: int=100):
        """Get recent trades for a specific stock symbol."""
        try:
            query = self._read_sql_file('get_recent_trades.sql')
            with self._connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol, limit))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error fetching recent trades: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise # Optionally re-raise the error if needed

    def insert_trade(self, symbol: str, price: decimal, trade_time: datetime): 
        """Insert a new trade into the database."""
        try:
            query = self._read_sql_file('insert_trade.sql')
            self._execute(query, (symbol, price, trade_time))
        except Exception as e:
            print(f"Error inserting trade: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise # Optionally re-raise the error if needed
        
