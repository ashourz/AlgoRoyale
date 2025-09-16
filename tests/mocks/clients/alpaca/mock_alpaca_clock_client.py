from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import (
    AlpacaClockClient,
)
from algo_royale.models.alpaca_trading.alpaca_clock import Clock
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaClockClient(AlpacaClockClient):
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

    async def fetch_clock(self):
        if self.throw_exception:
            raise Exception(
                "MockAlpacaClockClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return Clock(
            timestamp=1234567890,
            is_open=True,
            next_open="2024-09-15T09:30:00Z",
            next_close="2024-09-15T16:00:00Z",
        )

    async def aclose(self):
        pass
