from unittest.mock import AsyncMock

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stock_client import (
    AlpacaStockClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaStockClient(AlpacaStockClient):
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
        if endpoint == "stocks/quotes":
            return AsyncMock(
                return_value={
                    "quotes": {
                        "AAPL": [
                            {
                                "t": "2024-04-01T00:00:00Z",
                                "ax": "Q",
                                "ap": 150.0,
                                "as": 10,
                                "bx": "Q",
                                "bp": 149.5,
                                "bs": 12,
                                "c": [],
                                "z": "A",
                            }
                        ]
                    }
                }
            )()
        if endpoint == "stocks/quotes/latest":
            return AsyncMock(
                return_value={
                    "quotes": {
                        "AAPL": [
                            {
                                "t": "2024-04-01T00:00:00Z",
                                "ax": "Q",
                                "ap": 150.0,
                                "as": 10,
                                "bx": "Q",
                                "bp": 149.5,
                                "bs": 12,
                                "c": [],
                                "z": "A",
                            }
                        ]
                    }
                }
            )()
        if endpoint == "stocks/auctions":
            return AsyncMock(
                return_value={
                    "auctions": {
                        "AAPL": [
                            {
                                "d": "2024-04-01",
                                "o": [],
                                "c": [],
                            }
                        ]
                    }
                }
            )()
        if endpoint == "stocks/bars":
            return AsyncMock(
                return_value={
                    "bars": {
                        "AAPL": [
                            {
                                "t": "2022-01-03T09:30:00Z",
                                "o": 150.0,
                                "h": 151.0,
                                "l": 149.0,
                                "c": 150.5,
                                "v": 1000,
                                "n": 10,
                                "vw": 150.2,
                            }
                        ]
                    }
                }
            )()
        if endpoint == "stocks/bars/latest":
            return AsyncMock(
                return_value={
                    "bars": {
                        "AAPL": {
                            "t": "2022-01-03T09:30:00Z",
                            "o": 150.0,
                            "h": 151.0,
                            "l": 149.0,
                            "c": 150.5,
                            "v": 1000,
                            "n": 10,
                            "vw": 150.2,
                        }
                    }
                }
            )()
        if endpoint.startswith("stocks/meta/conditions/"):
            return AsyncMock(return_value={"A": "Regular Sale"})()
        if endpoint == "stocks/snapshots":
            return AsyncMock(
                return_value={
                    "AAPL": {
                        "latest_trade": {"price": 150.0, "size": 10},
                        "latest_quote": {"ask_price": 150.0, "bid_price": 149.5},
                        "minute_bar": {
                            "open_price": 150.0,
                            "close_price": 150.5,
                            "volume": 1000,
                        },
                        "daily_bar": {
                            "high_price": 151.0,
                            "low_price": 149.0,
                            "volume": 1000,
                        },
                        "previous_daily_bar": {
                            "high_price": 150.0,
                            "low_price": 148.0,
                            "volume": 900,
                        },
                    }
                }
            )()
        if endpoint == "stocks/trades":
            return AsyncMock(
                return_value={
                    "trades": {
                        "AAPL": [
                            {
                                "t": "2022-01-03T09:30:00Z",
                                "x": "Q",
                                "p": 150.0,
                                "s": 10,
                                "c": [],
                                "i": 1,
                                "z": "regular",
                            }
                        ]
                    }
                }
            )()
        if endpoint == "stocks/trades/latest":
            return AsyncMock(
                return_value={
                    "trades": {
                        "AAPL": {
                            "t": "2022-01-03T09:30:00Z",
                            "x": "Q",
                            "p": 150.0,
                            "s": 10,
                            "c": [],
                            "i": 1,
                            "z": "regular",
                        }
                    }
                }
            )()
        return AsyncMock(return_value={})()
