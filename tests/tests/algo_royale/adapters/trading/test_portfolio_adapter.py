import pytest

from tests.mocks.adapters.mock_portfolio_adapter import MockPortfolioAdapter


@pytest.fixture
def portfolio_adapter():
    adapter = MockPortfolioAdapter()
    yield adapter


@pytest.mark.asyncio
class TestPortfolioAdapter:
    async def test_get_portfolio_history(self, portfolio_adapter):
        result = await portfolio_adapter.get_portfolio_history()
        assert result is not None
        # PortfolioPerformance should have these attributes
        for attr in [
            "timestamp",
            "equity",
            "profit_loss",
            "profit_loss_pct",
            "base_value",
            "timeframe",
            "base_value_asof",
        ]:
            assert hasattr(result, attr)

    async def test_get_portfolio_history_empty(self, portfolio_adapter):
        portfolio_adapter.set_return_empty(True)
        result = await portfolio_adapter.get_portfolio_history()
        assert result is not None
        assert result.timestamp == []
        assert result.equity == []
        portfolio_adapter.reset_return_empty()
