from algo_royale.models.alpaca_trading.alpaca_clock import Clock
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaClockClient:
    def __init__(self):
        self.logger = MockLoggable()

    async def fetch_clock(self):
        return Clock(
            timestamp=1234567890,
            is_open=True,
            next_open="2024-09-15T09:30:00Z",
            next_close="2024-09-15T16:00:00Z",
        )

    async def aclose(self):
        pass
