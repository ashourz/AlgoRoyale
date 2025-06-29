from algo_royale.backtester.strategy.signal.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.backtester.strategy.signal.pullback_entry_strategy import (
    PullbackEntryStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class PullbackEntryStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Pullback Entry strategy.
    This strategy uses a combination of entry conditions based on pullback entries.
    It does not include any filter conditions, trend conditions, or exit conditions, focusing solely on the pullback entry logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [PullbackEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = []  # No exit conditions for this strategy
    allow_empty_entry = True  # Allow empty entry conditions
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = PullbackEntryStrategy
