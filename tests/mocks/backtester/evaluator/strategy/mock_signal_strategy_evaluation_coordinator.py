from unittest.mock import MagicMock

from algo_royale.backtester.evaluator.strategy.signal_strategy_evaluation_coordinator import (
    SignalStrategyEvaluationCoordinator,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSignalStrategyEvaluationCoordinator(SignalStrategyEvaluationCoordinator):
    def __init__(self):
        super().__init__(
            optimization_root=MagicMock(),
            evaluation_type="mock_eval_type",
            optimization_json_filename="mock_opt.json",
            evaluation_json_filename="mock_eval.json",
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
