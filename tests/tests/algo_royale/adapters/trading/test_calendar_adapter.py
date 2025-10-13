import pytest

from tests.mocks.adapters.mock_calendar_adapter import MockCalendarAdapter


@pytest.fixture
def calendar_adapter():
    adapter = MockCalendarAdapter()
    yield adapter


@pytest.mark.asyncio
class TestCalendarAdapter:
    async def test_get_calendar(self, calendar_adapter):
        result = await calendar_adapter.get_calendar()
        assert result is not None
        assert hasattr(result, "calendars")
        assert isinstance(result.calendars, list)
        assert all(hasattr(c, "trading_day") for c in result.calendars)

    async def test_get_calendar_empty(self, calendar_adapter):
        calendar_adapter.set_return_empty(True)
        result = await calendar_adapter.get_calendar()
        assert result is None or (
            hasattr(result, "calendars") and result.calendars == []
        )
        calendar_adapter.reset_return_empty()

    async def test_get_calendar_by_date(self, calendar_adapter):
        from datetime import datetime

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)
        result = await calendar_adapter.get_calendar_by_date(start, end)
        assert result is not None
        assert hasattr(result, "calendars")
        assert isinstance(result.calendars, list)
        assert all(hasattr(c, "trading_day") for c in result.calendars)

    async def test_get_calendar_by_date_empty(self, calendar_adapter):
        from datetime import datetime

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)
        calendar_adapter.set_return_empty(True)
        result = await calendar_adapter.get_calendar_by_date(start, end)
        assert result is None or (
            hasattr(result, "calendars") and result.calendars == []
        )
        calendar_adapter.reset_return_empty()
