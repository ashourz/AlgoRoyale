# src: tests/integration/client/test_alpaca_client.py

import pytest
from datetime import datetime, timezone
from algo_royale.shared.models.alpaca_market_data.alpaca_news import News, NewsResponse
from algo_royale.the_risk_is_not_enough.client.alpaca_market_data.alpaca_news_client import AlpacaNewsClient

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType


# Set up logging (prints to console)
logger = LoggerSingleton(LoggerType.TRADING, Environment.TEST).get_logger()

@pytest.fixture(scope="class")
def alpaca_client():
    return AlpacaNewsClient()

@pytest.mark.asyncio
class TestAlpacaNewsClientIntegration:

    def test_fetch_news(self, alpaca_client):
        """Test fetching news data from Alpaca's live endpoint."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 1, 0,0,0,tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = alpaca_client.fetch_news(
            symbols=symbols,
            # start_date=start_date,
            # end_date=end_date
        )

        assert result is not None
        assert isinstance(result, NewsResponse)
        assert len(result.news) > 0

        first_news = result.news[0]
        assert isinstance(first_news, News)

        expected_attrs = [
            "id", "author", "content", "created_at",
            "headline", "images", "source", "summary",
            "symbols", "updated_at", "url"
        ]
        for attr in expected_attrs:
            assert hasattr(first_news, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_news, attr) is not None, f"{attr} is None"            
            


