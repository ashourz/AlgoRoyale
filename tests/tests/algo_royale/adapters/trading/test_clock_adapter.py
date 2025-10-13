import pytest

from tests.mocks.adapters.mock_clock_adapter import MockClockAdapter


@pytest.fixture
def clock_adapter():
    adapter = MockClockAdapter()
    yield adapter


@pytest.mark.asyncio
class TestClockAdapter:
    async def test_get_clock(self, clock_adapter):
        result = await clock_adapter.get_clock()
        assert result is not None
        assert hasattr(result, "timestamp")

    async def test_get_clock_empty(self, clock_adapter):
        clock_adapter.set_return_empty(True)
        result = await clock_adapter.get_clock()
        assert result is None or result == {}
        clock_adapter.reset_return_empty()

    async def test_get_clock_exception(self, clock_adapter):
        clock_adapter.set_throw_exception(True)
        with pytest.raises(Exception):
            await clock_adapter.get_clock()
        clock_adapter.reset_throw_exception()
