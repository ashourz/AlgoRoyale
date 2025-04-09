# src/algo_royale/db/dao/news_sentiment_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO

class NewsSentimentDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_sentiment_by_trade_id(self, trade_id: int):
        return self.fetch("get_sentiment_by_trade_id.sql", (trade_id,))

    def insert_sentiment(self, trade_id: int, symbol: str, sentiment_score: decimal, headline: str, source: str, published_at: datetime):
        return self.insert(
            "insert_sentiment.sql",
            (trade_id, symbol, sentiment_score, headline, source, published_at)
        )

    def update_sentiment(self, sentiment_id: int, sentiment_score: decimal, headline: str, source: str, published_at: datetime):
        return self.update(
            "update_sentiment.sql",
            (sentiment_score, headline, source, published_at, sentiment_id)
        )

    def delete_sentiment(self, sentiment_id: int):
        return self.delete("delete_sentiment.sql", (sentiment_id,))
