from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.conditions.rsi_entry import RSIEntryCondition
from algo_royale.strategy_factory.conditions.rsi_exit import RSIExitCondition
from algo_royale.strategy_factory.strategies.rsi_strategy import RSIStrategy


class RSIStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for an RSI strategy.
    This strategy uses a combination of entry and exit conditions based on the Relative Strength Index (RSI).
    It does not include any filter conditions or trend conditions, focusing solely on the RSI logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [RSIEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [RSIExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = RSIStrategy
