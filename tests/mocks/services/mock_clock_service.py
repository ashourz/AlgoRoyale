from algo_royale.services.clock_service import ClockService
from algo_royale.utils.clock_provider import ClockProvider
from tests.mocks.adapters.mock_clock_adapter import MockClockAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockClockService(ClockService):
    async def schedule_job(self, job_name, run_time, coro_func):
        # Mock: do nothing, just return
        return None

    def __init__(self):
        super().__init__(
            clock_adapter=MockClockAdapter(),
            clock_provider=ClockProvider(),
            logger=MockLoggable(),
        )

        # Patch: add dummy scheduler with shutdown method

        class DummyScheduler:
            def start(self):
                pass

            def shutdown(self, wait=False):
                pass

        self.scheduler = DummyScheduler()

    async def async_get_market_clock(self):
        # Patch: return a mock object with open/close attributes
        class MockMarketClock:
            def __init__(self):
                from datetime import datetime, timedelta, timezone

                now = datetime.now(timezone.utc)
                self.open = now + timedelta(minutes=1)
                self.close = now + timedelta(hours=6)
                self.next_open = self.open + timedelta(days=1)
                self.next_close = self.close + timedelta(days=1)

        if hasattr(self, "return_empty") and self.return_empty:
            return None
        return MockMarketClock()

    def ensure_utc(self, dt):
        # Patch: just return the datetime as is
        return dt

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
