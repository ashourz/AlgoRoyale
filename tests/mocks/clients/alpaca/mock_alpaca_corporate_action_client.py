from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaCorporateActionClient(AlpacaCorporateActionClient):
    def __init__(self):
        self.logger = MockLoggable()  # Or use a mock logger if needed
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

    async def fetch_corporate_actions(
        self,
        symbols,
        start_date,
        end_date,
        cusips=None,
        types=None,
        ids=None,
        sort_order=None,
        page_limit=1000,
        page_token=None,
    ):
        from algo_royale.models.alpaca_market_data.alpaca_corporate_action import (
            CorporateActionResponse,
        )

        if self.throw_exception:
            raise Exception(
                "MockAlpacaCorporateActionClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            raw = {
                "corporate_actions": {},
                "next_page_token": None,
            }
            return CorporateActionResponse.from_raw(raw)
        # Return a mock response similar to the real client
        raw = {
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
        return CorporateActionResponse.from_raw(raw)

    async def aclose(self):
        pass
