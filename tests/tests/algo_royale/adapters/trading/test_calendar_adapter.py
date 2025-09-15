import pytest

from tests.mocks.adapters.mock_calendar_adapter import MockCalendarAdapter


@pytest.fixture
def calendar_adapter():
    adapter = MockCalendarAdapter()
    yield adapter


class TestCalendarAdapter:
    def test_get_calendar(self, calendar_adapter):
        result = pytest.run(calendar_adapter.get_calendar())
        assert result is not None
        assert isinstance(result, list)
        assert any("date" in c for c in result)

    def test_get_calendar_empty(self, calendar_adapter):
        calendar_adapter.set_return_empty(True)
        result = pytest.run(calendar_adapter.get_calendar())
        assert result == []
        calendar_adapter.reset_return_empty()
