import pytest

from tests.mocks.adapters.mock_assets_adapter import MockAssetsAdapter


@pytest.fixture
def assets_adapter():
    adapter = MockAssetsAdapter()
    yield adapter


@pytest.mark.asyncio
class TestAssetsAdapter:
    async def test_get_assets(self, assets_adapter):
        result = await assets_adapter.get_assets()
        assert isinstance(result, list)
        assert all(hasattr(a, "symbol") for a in result)

    async def test_get_asset_by_symbol(self, assets_adapter):
        result = await assets_adapter.get_asset_by_symbol("AAPL")
        assert result is not None
        assert hasattr(result, "symbol")

    async def test_get_assets_empty(self, assets_adapter):
        assets_adapter.set_return_empty(True)
        result = await assets_adapter.get_assets()
        assert result == []
        assets_adapter.reset_return_empty()
