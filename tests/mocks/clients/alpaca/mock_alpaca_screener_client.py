from unittest.mock import AsyncMock

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    AlpacaScreenerClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaScreenerClient(AlpacaScreenerClient):
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
        self.return_empty = False
        self.throw_exception = False

    def get(self, endpoint, params=None):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaScreenerClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return AsyncMock(return_value={})()
        return AsyncMock(
            return_value={
                "market_type": "gainers",
                "most_actives": [
                    {"symbol": "AAPL", "trade_count": 100, "volume": 10000},
                    {"symbol": "GOOG", "trade_count": 80, "volume": 8000},
                ],
                "gainers": [
                    {
                        "symbol": "AAPL",
                        "change": 5.0,
                        "percent_change": 2.5,
                        "price": 150.0,
                    }
                ],
                "losers": [
                    {
                        "symbol": "GOOG",
                        "change": -3.0,
                        "percent_change": -1.5,
                        "price": 120.0,
                    }
                ],
                "next_page_token": None,
                "last_updated": "2024-09-14T12:00:00Z",
            }
        )()
