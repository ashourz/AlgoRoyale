from algo_royale.adapters.trading.clock_adapter import ClockAdapter
from tests.mocks.clients.mock_alpaca_clock_client import MockAlpacaClockClient
from tests.mocks.mock_loggable import MockLoggable


class MockClockAdapter(ClockAdapter):
    def __init__(self):
        clock_client = MockAlpacaClockClient()
        logger = MockLoggable()
        super().__init__(clock_client=clock_client, logger=logger)

    def set_return_empty(self, value: bool):
        self.clock_client.return_empty = value

    def reset_return_empty(self):
        self.clock_client.return_empty = False

    def set_throw_exception(self, value: bool):
        self.clock_client.throw_exception = value

    def reset_throw_exception(self):
        self.clock_client.throw_exception = False
