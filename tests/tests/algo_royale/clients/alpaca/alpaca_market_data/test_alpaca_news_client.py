# src: tests/integration/client/test_alpaca_client.py


import pytest

from algo_royale.models.alpaca_market_data.alpaca_news import News, NewsResponse
from tests.mocks.clients.mock_alpaca_news_client import MockAlpacaNewsClient
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
async def alpaca_client():
    client = MockAlpacaNewsClient(logger=logger)
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaNewsClient:
    async def test_fetch_news(self, alpaca_client):
        """Test fetching news data from Alpaca using a mock response."""
        symbols = ["AAPL"]
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
