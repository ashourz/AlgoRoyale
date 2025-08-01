from algo_royale.backtester.strategy.signal.conditions.rsi_entry import (
    RSIEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_exit import RSIExitCondition
from algo_royale.backtester.strategy.signal.rsi_strategy import RSIStrategy
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class RSIStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for an RSI strategy.
    This strategy uses a combination of entry and exit conditions based on the Relative Strength Index (RSI).
    It does not include any filter conditions or trend conditions, focusing solely on the RSI logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=RSIStrategy,
            filter_condition_types=[],
            entry_condition_types=[RSIEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[RSIExitCondition],
            stateful_logic_types=[],
        )
