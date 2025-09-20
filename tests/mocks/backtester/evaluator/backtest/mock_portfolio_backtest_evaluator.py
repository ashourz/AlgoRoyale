from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioBacktestEvaluator(PortfolioBacktestEvaluator):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(logger=self.logger)
        self.raise_exception = False
        self.return_none = False
        self.result = {"mock": True}

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def set_return_none(self, value: bool):
        self.return_none = value

    def set_result(self, value):
        self.result = value

    def reset(self):
        self.raise_exception = False
        self.return_none = False
        self.result = {"mock": True}

    def reset_raise_exception(self):
        self.raise_exception = False

    def evaluate(self, *args, **kwargs):
        if self.raise_exception:
            raise Exception("Mocked exception in evaluate")
        if self.return_none:
            return None
        return self.result
