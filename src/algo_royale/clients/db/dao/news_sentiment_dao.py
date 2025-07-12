## db\dao\news_sentiment_dao.py
from datetime import datetime
from decimal import Decimal as Decimal
from typing import Tuple

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable


class NewsSentimentDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: Loggable,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_sentiment_by_trade_id(
        self, trade_id: int
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by trade ID."""
        return self.fetch("get_sentiment_by_trade_id.sql", (trade_id,))

    def fetch_sentiment_by_symbol(
        self, symbol: str
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol."""
        return self.fetch("get_sentiment_by_symbol.sql", (symbol,))

    def fetch_sentiment_by_symbol_and_date(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[Tuple[int, int, str, Decimal, str, str, datetime]]:
        """Fetch sentiment data by symbol and date range."""
        return self.fetch(
            "get_sentiment_by_symbol_and_date.sql", (symbol, start_date, end_date)
        )

    def insert_sentiment(
        self,
        trade_id: int,
        symbol: str,
        sentiment_score: Decimal,
        headline: str,
        source: str,
        published_at: datetime,
    ) -> None:
        """Insert a new sentiment record."""
        return self.insert(
            "insert_sentiment.sql",
            (trade_id, symbol, sentiment_score, headline, source, published_at),
        )

    def update_sentiment(
        self,
        sentiment_id: int,
        sentiment_score: Decimal,
        headline: str,
        source: str,
        published_at: datetime,
    ) -> None:
        """Update sentiment information."""
        return self.update(
            "update_sentiment.sql",
            (sentiment_score, headline, source, published_at, sentiment_id),
        )

    def delete_sentiment(self, sentiment_id: int) -> None:
        """Delete a sentiment record."""
        return self.delete("delete_sentiment.sql", (sentiment_id,))
