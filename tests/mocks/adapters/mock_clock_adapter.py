from algo_royale.adapters.trading.clock_adapter import ClockAdapter
from tests.mocks.clients.mock_alpaca_clock_client import MockAlpacaClockClient
from tests.mocks.mock_loggable import MockLoggable


class MockClockAdapter(ClockAdapter):
    def __init__(self):
        client = MockAlpacaClockClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_clock(self, *args, **kwargs):
        if self.return_empty:
            return None
        return {"timestamp": 1234567890, "is_open": True}
