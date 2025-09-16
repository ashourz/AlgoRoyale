from algo_royale.services.clock_service import ClockService
from tests.mocks.adapters.mock_clock_adapter import MockClockAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockClockService(ClockService):
    def __init__(self):
        super().__init__(
            clock_adapter=MockClockAdapter(),
            logger=MockLoggable(),
        )

    def set_return_empty(self, value: bool):
        self.clock_adapter.set_return_empty(value)

    def reset_return_empty(self):
        self.clock_adapter.reset_return_empty()

    def set_throw_exception(self, value: bool):
        self.clock_adapter.set_throw_exception(value)

    def reset_throw_exception(self):
        self.clock_adapter.reset_throw_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_throw_exception()
