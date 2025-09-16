import pytest

from tests.mocks.adapters.mock_portfolio_adapter import MockPortfolioAdapter


@pytest.fixture
def portfolio_adapter():
    adapter = MockPortfolioAdapter()
    yield adapter


@pytest.mark.asyncio
class TestPortfolioAdapter:
    async def test_get_portfolio(self, portfolio_adapter):
        result = await portfolio_adapter.get_portfolio()
        assert result is not None
        assert hasattr(result, "id")

    async def test_get_portfolio_empty(self, portfolio_adapter):
        portfolio_adapter.set_return_empty(True)
        result = await portfolio_adapter.get_portfolio()
        assert result is None or result == {}
        portfolio_adapter.reset_return_empty()
