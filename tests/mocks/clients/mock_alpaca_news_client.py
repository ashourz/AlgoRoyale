from unittest.mock import AsyncMock

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaNewsClient(AlpacaNewsClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )

    def get(self, endpoint, params=None):
        return AsyncMock(
            return_value={
                "news": [
                    {
                        "id": 1,
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
        )()
