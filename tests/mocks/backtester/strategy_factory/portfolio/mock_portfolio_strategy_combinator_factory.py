from algo_royale.backtester.strategy_factory.portfolio.portfolio_strategy_combinator_factory import (
    PortfolioStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioStrategyCombinatorFactory(PortfolioStrategyCombinatorFactory):
    def __init__(self):
        self.logger = MockLoggable()
        self.strategy_logger = MockLoggable()
        super().__init__(
            combinator_list_path="mock/path",
            logger=self.logger,
            strategy_logger=self.strategy_logger,
        )
        self.raise_exception = False
        self.return_none = False
        self.combinator_list = []

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def set_return_none(self, value: bool):
        self.return_none = value

    def set_combinator(self, value):
        self.combinator = value

    def reset(self):
        self.raise_exception = False
        self.return_none = False
        self.combinator = {"mock": True}

    def all_combinators(self):
        return self.combinator_list
