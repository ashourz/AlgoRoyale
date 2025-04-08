## db\dao\signal_dao.py
import decimal
import datetime
from db.dao.base_dao import BaseDAO
from db.db import connect_db

class SignalDAO(BaseDAO):
    def __init__(self):
        pass  # No need to keep a connection open permanently

    def get_signals_by_symbol(self, symbol: str):
        """Get signals for a specific stock symbol."""
        try:
            query = self._read_sql_file('get_signals_by_symbol.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error fetching signals: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise  # Optionally re-raise the error if needed


    def insert_signal(self, symbol: str, signal: str, price: decimal, created_at: datetime):
        """Insert a new signal into the database."""
        try:
            query = self._read_sql_file('insert_signal.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol, signal, price, created_at))
                    conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error inserting signal: {e}")
            # Log the error or re-raise it as needed
            raise  # Re-raise the exception to be handled higher up in the call stack the call stackck