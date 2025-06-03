from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.strategy_factory.strategies.pullback_entry_strategy import (
    PullbackEntryStrategy,
)


class PullbackEntryStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Pullback Entry strategy.
    This strategy uses a combination of entry conditions based on pullback entries.
    It does not include any filter conditions, trend conditions, or exit conditions, focusing solely on the pullback entry logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [PullbackEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = []  # No exit conditions for this strategy
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = PullbackEntryStrategy
