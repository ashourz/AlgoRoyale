import pytest

from tests.mocks.services.mock_clock_service import MockClockService


@pytest.fixture
def clock_service():
    service = MockClockService()
    yield service


@pytest.mark.asyncio
class TestClockService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, clock_service: MockClockService):
        print("Setup")
        clock_service.reset()
        yield
        print("Teardown")
        clock_service.reset()

    async def test_start_and_stop(self, clock_service):
        # Should not raise
        clock_service.start()
        await clock_service.async_stop()

    def test_get_system_utc_time(self, clock_service):
        now = clock_service.get_system_utc_time()
        from datetime import timezone

        assert now.tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_async_get_market_clock(self, clock_service):
        # Should return a mock Clock object
        clock = await clock_service.async_get_market_clock()
        assert clock is not None

    def test_ensure_utc(self, clock_service):
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
    async def test_schedule_job(self, clock_service):
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
