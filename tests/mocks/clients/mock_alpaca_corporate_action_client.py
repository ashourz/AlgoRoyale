from unittest.mock import AsyncMock

from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)


class MockAlpacaCorporateActionClient(AlpacaCorporateActionClient):
    def __init__(self, logger):
        super().__init__(
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

    def get(self, endpoint, params=None):
        return AsyncMock(
            return_value={
                "corporate_actions": {
                    "AAPL": [
                        {
                            "ex_date": "2024-04-01T00:00:00Z",
                            "foreign": False,
                            "payable_date": "2024-04-15T00:00:00Z",
                            "process_date": "2024-04-16T00:00:00Z",
                            "rate": 0.5,
                            "record_date": "2024-03-31T00:00:00Z",
                            "special": False,
                            "symbol": "AAPL",
                        }
                    ]
                },
                "next_page_token": None,
            }
        )()
