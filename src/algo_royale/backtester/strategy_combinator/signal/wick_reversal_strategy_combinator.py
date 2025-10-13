from algo_royale.backtester.strategy.signal.conditions.wick_reversal_entry import (
    WickReversalEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.wick_reversal_exit import (
    WickReversalExitCondition,
)
from algo_royale.backtester.strategy.signal.wick_reversal_strategy import (
    WickReversalStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class WickReversalStrategyCombinator(SignalStrategyCombinator):
    """
    Combines conditions and logic for a Wick Reversal strategy.
    This strategy uses a combination of entry conditions based on wick reversals,
    trend conditions based on volume surges, and exit conditions based on wick reversals.
    It does not include any filter conditions or stateful logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=WickReversalStrategy,
            filter_condition_types=[],
            entry_condition_types=[WickReversalEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[WickReversalExitCondition],
            stateful_logic_types=[],
        )
