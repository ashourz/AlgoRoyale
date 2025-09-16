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
        assert isinstance(result, list)
        assert all(hasattr(c, "date") for c in result)

    async def test_get_calendar_empty(self, calendar_adapter):
        calendar_adapter.set_return_empty(True)
        result = await calendar_adapter.get_calendar()
        assert result == []
        calendar_adapter.reset_return_empty()
