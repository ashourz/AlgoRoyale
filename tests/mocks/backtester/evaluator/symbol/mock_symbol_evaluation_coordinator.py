from unittest.mock import MagicMock

from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSymbolEvaluationCoordinator(SymbolEvaluationCoordinator):
    def __init__(self):
        super().__init__(
            optimization_root=MagicMock(),
            evaluation_json_filename="mock_eval.json",
            summary_json_filename="mock_summary.json",
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
