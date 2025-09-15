import pytest

from tests.mocks.adapters.mock_positions_adapter import MockPositionsAdapter


@pytest.fixture
def positions_adapter():
    adapter = MockPositionsAdapter()
    yield adapter


class TestPositionsAdapter:
    def test_get_positions(self, positions_adapter):
        result = pytest.run(positions_adapter.get_positions())
        assert result is not None
        assert isinstance(result, list)
        assert any("symbol" in p for p in result)

    def test_get_positions_empty(self, positions_adapter):
        positions_adapter.set_return_empty(True)
        result = pytest.run(positions_adapter.get_positions())
        assert result == []
        positions_adapter.reset_return_empty()
