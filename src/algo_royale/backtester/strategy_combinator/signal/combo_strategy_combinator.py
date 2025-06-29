from algo_royale.backtester.strategy.signal.combo_strategy import ComboStrategy
from algo_royale.backtester.strategy.signal.conditions.combo_entry import (
    ComboEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_exit import (
    ComboExitCondition,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class ComboStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Combo strategy.
    This strategy uses a combination of entry and exit conditions based on multiple indicators.
    It does not include any filter conditions or trend conditions, focusing solely on the combo logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [ComboEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [ComboExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = ComboStrategy
