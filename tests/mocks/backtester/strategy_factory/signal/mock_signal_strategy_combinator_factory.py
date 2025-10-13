from algo_royale.backtester.strategy_factory.signal.signal_strategy_combinator_factory import (
    SignalStrategyCombinatorFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSignalStrategyCombinatorFactory(SignalStrategyCombinatorFactory):
    def __init__(self, combinator_list_path=None, logger=None, strategy_logger=None):
        # Accept the same arguments as the real factory, but allow them to be optional for test flexibility
        self.logger = logger or MockLoggable()
        self.strategy_logger = strategy_logger or MockLoggable()
        # Use a dummy path if not provided
        super().__init__(
            combinator_list_path=combinator_list_path or "mock/path",
            logger=self.logger,
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
