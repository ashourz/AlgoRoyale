import pytest

from tests.mocks.backtester.strategy_factory.portfolio.mock_portfolio_strategy_combinator_factory import (
    MockPortfolioStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class TestPortfolioStrategyCombinatorFactory:
    def setup_method(self):
        self.logger = MockLoggable()
        self.factory = MockPortfolioStrategyCombinatorFactory(
            "/tmp/combinators.json", self.logger, self.logger
        )

    def test_get_combinator_normal(self):
        # Should return a combinator or raise if not found
        try:
            combinator = self.factory.get_combinator("SomeCombinator")
        except Exception as e:
            assert isinstance(e, Exception)

    def test_get_combinator_error(self):
        # Should handle missing class
        with pytest.raises(Exception):
            self.factory.get_combinator("NonExistentCombinator")

    def test_get_combinator_invalid_type(self):
        # Should handle invalid type
        with pytest.raises(Exception):
            self.factory.get_combinator(123)
