# src: tests/integration/client/test_alpaca_client.py

import logging
from datetime import datetime, timezone

import pytest

from algo_royale.adapters.market_data.news_adapter import NewsAdapter
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.di import application_container
from algo_royale.di.adapter.adapter_container import AdapterContainer

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    application: application_container.ApplicationContainer = application_container()
    adapters: AdapterContainer = application.adapter_container()
    news_adapter: NewsAdapter = adapters.news_adapter()
    client: AlpacaNewsClient = news_adapter.client()
    return client


@pytest.mark.asyncio
class TestAlpacaNewsClientIntegration:
    def test_fetch_news(self, alpaca_client):
        """Test fetching news data from Alpaca's live endpoint."""
        symbols = ["AAPL", "GOOGL"]
        start_date = datetime(2024, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = alpaca_client.fetch_news(
            symbols=symbols, start_date=start_date, end_date=end_date
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
