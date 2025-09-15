import pytest

from tests.mocks.adapters.mock_assets_adapter import MockAssetsAdapter


@pytest.fixture
def assets_adapter():
    adapter = MockAssetsAdapter()
    yield adapter


class TestAssetsAdapter:
    def test_get_assets(self, assets_adapter):
        result = pytest.run(assets_adapter.get_assets())
        assert result is not None
        assert isinstance(result, list)
        assert any("symbol" in a for a in result)

    def test_get_assets_empty(self, assets_adapter):
        assets_adapter.set_return_empty(True)
        result = pytest.run(assets_adapter.get_assets())
        assert result == []
        assets_adapter.reset_return_empty()
