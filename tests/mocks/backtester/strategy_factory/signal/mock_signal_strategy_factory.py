from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_condition import (
    BufferedStrategyCondition,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_signal_strategy import (
    BufferedSignalStrategy,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_stateful_logic import (
    BufferedStatefulLogic,
)
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.backtester.strategy_factory.signal.signal_strategy_factory import (
    SignalStrategyFactory,
)
from tests.mocks.mock_loggable import MockLoggable


class MockSignalStrategyFactory(SignalStrategyFactory):
    def __init__(self):
        self.logger = MockLoggable()
        self.strategy_logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            strategy_logger=self.strategy_logger,
        )
        self.return_empty = False
        self.raise_exception = False
        self.default_base_signal_strategy = BaseSignalStrategy(
            logger=self.strategy_logger,
        )
        self.default_buffered_signal_strategy = BufferedSignalStrategy(
            strategy_type=BaseSignalStrategy,
            logger=self.strategy_logger,
        )
        self.buffered_signal_strategy = self.default_buffered_signal_strategy
        self.base_signal_strategy = self.default_base_signal_strategy
        self.default_buffered_strategy_condition = BufferedStrategyCondition(
            condition=StrategyCondition(
                logger=self.strategy_logger,
            ),
            window_size=1,
            logger=self.strategy_logger,
        )
        self.buffered_strategy_condition = self.default_buffered_strategy_condition
        self.default_stateful_logic = StatefulLogic(
            logger=self.strategy_logger,
        )
        self.stateful_logic = self.default_stateful_logic
        self.default_buffered_stateful_logic = BufferedStatefulLogic(
            stateful_logic=self.stateful_logic,
            window_size=1,
            logger=self.strategy_logger,
        )
        self.buffered_stateful_logic = self.default_buffered_stateful_logic

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset(self):
        self.return_empty = False
        self.raise_exception = False
        self.base_signal_strategy = self.default_base_signal_strategy
        self.buffered_strategy_condition = self.default_buffered_strategy_condition
        self.stateful_logic = self.default_stateful_logic
        self.buffered_stateful_logic = self.default_buffered_stateful_logic
        self.buffered_signal_strategy = self.default_buffered_signal_strategy

    def instantiate_conditions(self, cond_list):
        if self.raise_exception:
            raise Exception("Mocked exception in instantiate_conditions")
        if self.return_empty:
            return []
        return [self.base_signal_strategy]

    def instantiate_buffered_conditions(self, cond_list):
        if self.raise_exception:
            raise Exception("Mocked exception in instantiate_buffered_conditions")
        if self.return_empty:
            return []
        return [self.buffered_strategy_condition]

    def instantiate_buffered_stateful_logic(self, logic):
        if self.raise_exception:
            raise Exception("Mocked exception in instantiate_stateful_logic")
        if self.return_empty:
            return []
        return [self.buffered_stateful_logic]

    def instantiate_stateful_logic(self, logic):
        if self.raise_exception:
            raise Exception("Mocked exception in instantiate_stateful_logic")
        if self.return_empty:
            return []
        return [self.stateful_logic]

    def build_strategy(self, strategy_class, params):
        if self.raise_exception:
            raise Exception("Mocked exception in build_strategy")
        if self.return_empty:
            return None
        return self.base_signal_strategy

    def build_buffered_strategy(self, strategy_class, params):
        if self.raise_exception:
            raise Exception("Mocked exception in build_buffered_strategy")
        if self.return_empty:
            return None
        return self.buffered_signal_strategy
