## db\dao\news_sentiment_dao.py
from algo_royale.live_trading.db.dao.base_dao import BaseDAO
from decimal import Decimal as Decimal
from datetime import datetime
from typing import List, Tuple

class NewsSentimentDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_sentiment_by_trade_id(self, trade_id: int) -> List[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by trade ID."""
        return self.fetch("get_sentiment_by_trade_id.sql", (trade_id,))
    
    def fetch_sentiment_by_symbol(self, symbol: str) -> List[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol."""
        return self.fetch("get_sentiment_by_symbol.sql", (symbol,))
    
    def fetch_sentiment_by_symbol_and_date(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol and date range."""
        return self.fetch("get_sentiment_by_symbol_and_date.sql", (symbol, start_date, end_date))
    
    def insert_sentiment(self, trade_id: int, symbol: str, sentiment_score: Decimal, headline: str, source: str, published_at: datetime) -> None:
        """Insert a new sentiment record."""
        return self.insert(
            "insert_sentiment.sql",
            (trade_id, symbol, sentiment_score, headline, source, published_at)
        )

    def update_sentiment(self, sentiment_id: int, sentiment_score: Decimal, headline: str, source: str, published_at: datetime) -> None:
        """Update sentiment information."""
        return self.update(
            "update_sentiment.sql",
            (sentiment_score, headline, source, published_at, sentiment_id)
        )

    def delete_sentiment(self, sentiment_id: int) -> None:
        """Delete a sentiment record."""
        return self.delete("delete_sentiment.sql", (sentiment_id,))

