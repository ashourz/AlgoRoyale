import pytest

from tests.mocks.adapters.mock_positions_adapter import MockPositionsAdapter


@pytest.fixture
def positions_adapter():
    adapter = MockPositionsAdapter()
    yield adapter


@pytest.mark.asyncio
class TestPositionsAdapter:
    async def test_fetch_all_open_positions(self, positions_adapter):
        result = await positions_adapter.fetch_all_open_positions()
        assert result is not None
        assert hasattr(result, "positions")
        assert isinstance(result.positions, list)

    async def test_get_open_position_by_symbol_or_asset_id(self, positions_adapter):
        result = await positions_adapter.get_open_position_by_symbol_or_asset_id("AAPL")
        assert result is not None
        assert hasattr(result, "positions")

    async def test_close_position_by_symbol_or_asset_id(self, positions_adapter):
        result = await positions_adapter.close_position_by_symbol_or_asset_id("AAPL")
        assert result is not None
        assert hasattr(result, "closedPositions")

    async def test_close_all_positions(self, positions_adapter):
        result = await positions_adapter.close_all_positions()
        assert result is not None
        assert hasattr(result, "closedPositions")

    async def test_fetch_all_open_positions_empty(self, positions_adapter):
        positions_adapter.set_return_empty(True)
        result = await positions_adapter.fetch_all_open_positions()
        assert result is not None
        assert result.positions == []
        positions_adapter.reset_return_empty()

    async def test_get_open_position_by_symbol_or_asset_id_empty(
        self, positions_adapter
    ):
        positions_adapter.set_return_empty(True)
        result = await positions_adapter.get_open_position_by_symbol_or_asset_id("AAPL")
        assert result is not None
        assert result.positions == []
        positions_adapter.reset_return_empty()

    async def test_close_position_by_symbol_or_asset_id_empty(self, positions_adapter):
        positions_adapter.set_return_empty(True)
        result = await positions_adapter.close_position_by_symbol_or_asset_id("AAPL")
        assert result is not None
        assert result.closedPositions == []
        positions_adapter.reset_return_empty()

    async def test_close_all_positions_empty(self, positions_adapter):
        positions_adapter.set_return_empty(True)
        result = await positions_adapter.close_all_positions()
        assert result is not None
        assert result.closedPositions == []
        positions_adapter.reset_return_empty()
