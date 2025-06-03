from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.wick_reversal_entry import (
    WickReversalEntryCondition,
)
from algo_royale.strategy_factory.conditions.wick_reversal_exit import (
    WickReversalExitCondition,
)
from algo_royale.strategy_factory.strategies.wick_reversal_strategy import (
    WickReversalStrategy,
)


class WickReversalStrategyCombinator(StrategyCombinator):
    """
    Combines conditions and logic for a Wick Reversal strategy.
    This strategy uses a combination of entry conditions based on wick reversals,
    trend conditions based on volume surges, and exit conditions based on wick reversals.
    It does not include any filter conditions or stateful logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [WickReversalEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = [WickReversalExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = WickReversalStrategy
