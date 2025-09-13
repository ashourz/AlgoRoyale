# src: tests/integration/client/test_alpaca_client.py


from unittest.mock import AsyncMock

import pytest

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.models.alpaca_market_data.alpaca_news import News, NewsResponse
from tests.mocks.mock_loggable import MockLoggable

logger = MockLoggable()


@pytest.fixture
async def alpaca_client(monkeypatch):
    client = AlpacaNewsClient(
        logger=logger,
        base_url="https://mock.alpaca.markets",
        api_key="fake_key",
        api_secret="fake_secret",
        api_key_header="APCA-API-KEY-ID",
        api_secret_header="APCA-API-SECRET-KEY",
        http_timeout=5,
        reconnect_delay=1,
        keep_alive_timeout=5,
    )
    # Patch the get method to return a fake response
    fake_response = {
        "news": [
            {
                "id": "news_1",
                "author": "Test Author",
                "content": "Test content",
                "created_at": "2024-04-01T00:00:00Z",
                "headline": "Test Headline",
                "images": [],
                "source": "Test Source",
                "summary": "Test summary",
                "symbols": ["AAPL"],
                "updated_at": "2024-04-01T01:00:00Z",
                "url": "https://example.com/news/1",
            }
        ],
        "next_page_token": None,
    }
    monkeypatch.setattr(client, "get", AsyncMock(return_value=fake_response))
    yield client
    await client.aclose()


@pytest.mark.asyncio
class TestAlpacaNewsClient:
    async def test_fetch_news(self, alpaca_client: AlpacaNewsClient):
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
