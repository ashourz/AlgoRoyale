## service\news_sentiment_service.py
from datetime import datetime
from decimal import Decimal
from typing import Tuple

from algo_royale.repo.news_sentiment_repo import NewsSentimentRepo


class NewsSentimentService:
    def __init__(self, repo: NewsSentimentRepo):
        self.repo = repo

    def insert_sentiment(
        self,
        trade_id: int,
        symbol: str,
        sentiment_score: Decimal,
        headline: str,
        source: str,
        published_at: datetime,
    ) -> None:
        """Insert sentiment data for a trade."""
        self.repo.insert_sentiment(
            trade_id, symbol, sentiment_score, headline, source, published_at
        )

    def get_sentiment_by_trade_id(
        self, trade_id: int
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by trade ID."""
        return self.repo.fetch_sentiment_by_trade_id(trade_id)

    def get_sentiment_by_symbol(
        self, symbol: str
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol."""
        return self.repo.fetch_sentiment_by_symbol(symbol)

    def get_sentiment_by_symbol_and_date(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol and date range."""
        return self.repo.fetch_sentiment_by_symbol_and_date(
            symbol, start_date, end_date
        )

    def update_sentiment(
        self,
        sentiment_id: int,
        sentiment_score: Decimal,
        headline: str,
        source: str,
        published_at: datetime,
    ) -> None:
        """Update sentiment data."""
        self.repo.update_sentiment(
            sentiment_id, sentiment_score, headline, source, published_at
        )

    def delete_sentiment(self, sentiment_id: int) -> None:
        """Delete sentiment data."""
        self.repo.delete_sentiment(sentiment_id)
