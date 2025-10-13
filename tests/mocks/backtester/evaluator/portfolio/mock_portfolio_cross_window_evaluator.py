from pathlib import Path

from algo_royale.backtester.evaluator.portfolio.portfolio_cross_window_evaluator import (
    PortfolioCrossWindowEvaluator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioCrossWindowEvaluator(PortfolioCrossWindowEvaluator):
    def __init__(self):
        super().__init__(logger=MockLoggable(), window_json_filename="mock.json")
        self.run_called = False
        self.return_value = {"mock": True}
        self.raise_exception = False

    def set_return_value(self, value):
        self.return_value = value

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def run(self, strategy_dir: Path):
        self.run_called = True
        if self.raise_exception:
            raise RuntimeError("Mocked exception in run")
        return self.return_value
