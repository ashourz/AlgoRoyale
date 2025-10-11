import pytest

from algo_royale.services.clock_service import ClockService
from algo_royale.utils.clock_provider import ClockProvider
from tests.mocks.adapters.mock_clock_adapter import MockClockAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.services.mock_clock_service import MockClockService


@pytest.fixture
def clock_service():
    service = ClockService(
        clock_adapter=MockClockAdapter(),
        clock_provider=ClockProvider(),
        logger=MockLoggable(),
    )
    yield service


def set_clock_service_raise_exception(clock_service: ClockService, value: bool):
    clock_service.clock_adapter.set_throw_exception(value)


def reset_clock_service_raise_exception(clock_service: ClockService):
    clock_service.clock_adapter.reset_throw_exception()


def set_clock_service_return_empty(clock_service: ClockService, value: bool):
    clock_service.clock_adapter.set_return_empty(value)


def reset_clock_service_return_empty(clock_service: ClockService):
    clock_service.clock_adapter.reset_return_empty()


def reset_clock_service(clock_service: ClockService):
    reset_clock_service_raise_exception(clock_service)
    reset_clock_service_return_empty(clock_service)


@pytest.mark.asyncio
class TestClockService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, clock_service: MockClockService):
        print("Setup")
        reset_clock_service(clock_service)
        yield
        print("Teardown")
        reset_clock_service(clock_service)

    def test_now(self, clock_service: ClockService):
        now = clock_service.now()
        from datetime import timezone

        assert now.tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_async_get_market_clock(self, clock_service: ClockService):
        # Should return a mock Clock object
        clock = await clock_service.async_get_market_clock()
        assert clock is not None

    def test_ensure_utc(self, clock_service: ClockService):
        from datetime import datetime, timezone

        # Already UTC
        dt_utc = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert clock_service.ensure_utc(dt_utc) == dt_utc
        # Naive returns None
        dt_naive = datetime(2024, 1, 1)
        assert clock_service.ensure_utc(dt_naive) is None
        # Non-UTC tz-aware
        import pytz

        dt_est = pytz.timezone("US/Eastern").localize(datetime(2024, 1, 1, 12, 0, 0))
        dt_est_to_utc = clock_service.ensure_utc(dt_est)
        assert dt_est_to_utc.tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_schedule_job(self, clock_service: ClockService):
        # Schedule a job in the past (should run immediately)
        import asyncio
        from datetime import datetime, timedelta, timezone

        ran = []

        async def dummy_job():
            ran.append(True)

        run_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        clock_service.schedule_job("test_job", dummy_job, run_time)
        # Give event loop a chance to run
        await asyncio.sleep(0.1)
        assert ran
