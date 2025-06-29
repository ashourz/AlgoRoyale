# src: tests/integration/client/test_alpaca_client.py

from datetime import datetime, timezone

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.di.container import DIContainer
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_singleton import LoggerSingleton, LoggerType
from algo_royale.models.alpaca_market_data.alpaca_news import News, NewsResponse

# Set up logging (prints to console)
logger = LoggerSingleton.get_instance(LoggerType.TRADING, LoggerEnv.TEST)


@pytest.fixture
async def alpaca_client(event_loop):
    client = AlpacaNewsClient(
        trading_config=DIContainer.trading_config(),
    )
    yield client
    await client.aclose()  # Clean up the async client


@pytest.mark.asyncio
class TestAlpacaNewsClientIntegration:
    async def test_fetch_news(self, alpaca_client: AlpacaNewsClient):
        """Test fetching news data from Alpaca's live endpoint."""
        symbols = ["AAPL"]
        start_date = datetime(2024, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = await alpaca_client.fetch_news(
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
            "id",
            "author",
            "content",
            "created_at",
            "headline",
            "images",
            "source",
            "summary",
            "symbols",
            "updated_at",
            "url",
        ]
        for attr in expected_attrs:
            assert hasattr(first_news, attr), f"Missing expected attribute: {attr}"
            assert getattr(first_news, attr) is not None, f"{attr} is None"
