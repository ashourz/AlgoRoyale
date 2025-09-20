from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactory,
)


class MockPortfolioStrategyOptimizerFactory(PortfolioStrategyOptimizerFactory):
    def __init__(self):
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}
        self.raise_exception = False

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    def reset_raise_exception(self):
        self.should_raise = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def create(self, *args, **kwargs):
        if self.should_raise:
            raise RuntimeError("Mocked exception in create")
        if self.should_return_none:
            return None
        return self.return_value
