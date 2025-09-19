from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactory,
)


class MockSignalStrategyOptimizerFactory(SignalStrategyOptimizerFactory):
    def __init__(self):
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    def create(self, *args, **kwargs):
        if self.should_raise:
            raise RuntimeError("Mocked exception in create")
        if self.should_return_none:
            return None
        return self.return_value
