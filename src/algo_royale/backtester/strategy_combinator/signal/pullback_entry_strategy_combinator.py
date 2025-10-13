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

    def __init__(self):
        super().__init__(
            strategy_class=PullbackEntryStrategy,
            filter_condition_types=[],
            entry_condition_types=[PullbackEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[],
            stateful_logic_types=[],
        )
