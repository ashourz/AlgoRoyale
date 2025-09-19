from unittest.mock import MagicMock

from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioEvaluationCoordinator(PortfolioEvaluationCoordinator):
    def __init__(self):
        super().__init__(
            cross_window_evaluator=MagicMock(),
            cross_strategy_summary=MagicMock(),
            optimization_root=MagicMock(),
            logger=MockLoggable(),
        )
        self.run_called = False
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    def run(self):
        self.run_called = True
        if self.should_raise:
            raise RuntimeError("Mocked exception in run")
        if self.should_return_none:
            return None
        return self.return_value
