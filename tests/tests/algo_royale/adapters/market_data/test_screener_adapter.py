import pytest

from tests.mocks.adapters.mock_screener_adapter import MockScreenerAdapter


@pytest.fixture
def screener_adapter():
    adapter = MockScreenerAdapter()
    yield adapter


@pytest.mark.asyncio
class TestScreenerAdapter:
    async def test_get_screened_symbols(self, screener_adapter):
        result = await screener_adapter.get_screened_symbols()
        assert result is not None
        assert isinstance(result, list)
        assert "AAPL" in result

    async def test_get_screened_symbols_empty(self, screener_adapter):
        screener_adapter.set_return_empty(True)
        result = await screener_adapter.get_screened_symbols()
        assert result == []
        screener_adapter.reset_return_empty()

    async def test_get_most_active_stocks(self, screener_adapter):
        from algo_royale.models.alpaca_market_data.enums import ActiveStockFilter

        result = await screener_adapter.get_most_active_stocks(
            ActiveStockFilter.VOLUME, top=2
        )
        assert result is not None
        assert hasattr(result, "most_actives")
        assert isinstance(result.most_actives, list)

    async def test_get_market_movers(self, screener_adapter):
        result = await screener_adapter.get_market_movers(top=2)
        assert result is not None
        assert hasattr(result, "gainers")
        assert hasattr(result, "losers")
        assert isinstance(result.gainers, list)
        assert isinstance(result.losers, list)
