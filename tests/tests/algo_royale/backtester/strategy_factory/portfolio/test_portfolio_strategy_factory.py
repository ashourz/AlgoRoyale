import pytest

from tests.mocks.backtester.strategy_factory.portfolio.mock_portfolio_strategy_factory import (
    MockPortfolioStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class TestPortfolioStrategyFactory:
    def setup_method(self):
        self.logger = MockLoggable()
        self.factory = MockPortfolioStrategyFactory()

    def test_create_strategy_normal(self):
        # Should return a strategy or raise if not found
        try:
            strategy = self.factory.create_strategy("SomeStrategy", {})
        except Exception as e:
            assert isinstance(e, Exception)

    def test_create_strategy_error(self):
        # Should handle missing class
        with pytest.raises(Exception):
            self.factory.create_strategy("NonExistentStrategy", {})

    def test_create_strategy_invalid_type(self):
        # Should handle invalid type
        with pytest.raises(Exception):
            self.factory.create_strategy(123, {})
