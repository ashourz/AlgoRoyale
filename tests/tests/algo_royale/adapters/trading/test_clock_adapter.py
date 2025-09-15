import pytest

from tests.mocks.adapters.mock_clock_adapter import MockClockAdapter


@pytest.fixture
def clock_adapter():
    adapter = MockClockAdapter()
    yield adapter


class TestClockAdapter:
    def test_get_clock(self, clock_adapter):
        result = pytest.run(clock_adapter.get_clock())
        assert result is not None
        assert "timestamp" in result

    def test_get_clock_empty(self, clock_adapter):
        clock_adapter.set_return_empty(True)
        result = pytest.run(clock_adapter.get_clock())
        assert result is None
        clock_adapter.reset_return_empty()
