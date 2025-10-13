from pathlib import Path

from algo_royale.backtester.evaluator.portfolio.portfolio_cross_strategy_summary import (
    PortfolioCrossStrategySummary,
)
from tests.mocks.mock_loggable import MockLoggable


class MockPortfolioCrossStrategySummary(PortfolioCrossStrategySummary):
    def __init__(self):
        super().__init__(logger=MockLoggable())
        self.run_called = False
        self.return_value = {"mock": True}
        self.raise_exception = False

    def set_return_value(self, value):
        self.return_value = value

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def run(self, symbol_dir: Path):
        self.run_called = True
        if self.raise_exception:
            raise RuntimeError("Mocked exception in run")
        return self.return_value
