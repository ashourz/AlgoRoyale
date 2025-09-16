import pytest

from tests.mocks.adapters.mock_positions_adapter import MockPositionsAdapter


@pytest.fixture
def positions_adapter():
    adapter = MockPositionsAdapter()
    yield adapter


@pytest.mark.asyncio
class TestPositionsAdapter:
    async def test_get_positions(self, positions_adapter):
        result = await positions_adapter.get_positions()
        assert isinstance(result, list)
        assert all(hasattr(p, "symbol") for p in result)

    async def test_get_position_by_symbol(self, positions_adapter):
        result = await positions_adapter.get_position_by_symbol("AAPL")
        assert result is not None
        assert hasattr(result, "symbol")

    async def test_get_positions_empty(self, positions_adapter):
        positions_adapter.set_return_empty(True)
        result = await positions_adapter.get_positions()
        assert result == []
        positions_adapter.reset_return_empty()
