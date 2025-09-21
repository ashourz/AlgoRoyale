# src: tests/integration/client/test_alpaca_client.py

import logging
from datetime import datetime, timezone

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.di.adapter.client_container import ClientContainer
from algo_royale.di.application_container import ApplicationContainer
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.models.alpaca_market_data.alpaca_news import News, NewsResponse

# Set up logging (prints to console)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def alpaca_client():
    application = ApplicationContainer(environment=ApplicationEnv.DEV_INTEGRATION)
    application.setup_configs()
    client_container: ClientContainer = (
        application.adapter_container().client_container()
    )
    client: AlpacaNewsClient = client_container.alpaca_news_client()
    return client


@pytest.mark.asyncio
class TestAlpacaNewsClientIntegration:
    async def test_fetch_news(self, alpaca_client: AlpacaNewsClient):
        """Test fetching news data from Alpaca's live endpoint."""
        symbols = ["AAPL", "GOOGL"]
        start_date = datetime(2024, 4, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = await alpaca_client.async_fetch_news(
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
