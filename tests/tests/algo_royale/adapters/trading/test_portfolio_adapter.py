import pytest

from tests.mocks.adapters.mock_portfolio_adapter import MockPortfolioAdapter


@pytest.fixture
def portfolio_adapter():
    adapter = MockPortfolioAdapter()
    yield adapter


class TestPortfolioAdapter:
    def test_get_portfolio(self, portfolio_adapter):
        result = pytest.run(portfolio_adapter.get_portfolio())
        assert result is not None
        assert "portfolio_value" in result

    def test_get_portfolio_empty(self, portfolio_adapter):
        portfolio_adapter.set_return_empty(True)
        result = pytest.run(portfolio_adapter.get_portfolio())
        assert result is None
        portfolio_adapter.reset_return_empty()
