## db\dao\news_sentiment_dao.py
import decimal
import datetime
from algo_royale.db.dao.base_dao import BaseDAO
from algo_royale.db.db import connect_db

class NewsSentimentDao(BaseDAO):
    def __init__(self):
        pass # No need to keep a connection open permanently
    
    def get_news_sentiment_by_symbol(self, symbol: str):
        """Get news sentiment for a specific stock symbol."""
        try:
            query = self._read_sql_file('get_news_sentiment_by_symbol.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (symbol,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error fetching news sentiment: {e}")
            # Here you might want to log the error to a file or monitoring system
            raise
            # Re-raise the exception to be handled higher up in the call stack
        
    def insert_news_sentiment(self, trade_id: int, symbol: str, sentiment_Score: decimal, headline: str, source: str, published_at: datetime):
        """Insert a new news sentiment into the database."""
        try:
            query = self._read_sql_file('insert_news_sentiment.sql')
            with connect_db() as conn:  # Automatically manage connection
                with conn.cursor() as cur:  # Automatically manage cursor
                    cur.execute(query, (trade_id, symbol, sentiment_Score, headline, source, published_at))
                    conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error inserting news sentiment: {e}")
            # Log the error or re-raise it as needed
            raise
            # Re-raise the exception to be handled higher up in the call stack
    