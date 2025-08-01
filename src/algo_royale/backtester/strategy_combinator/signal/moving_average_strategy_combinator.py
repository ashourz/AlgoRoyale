from algo_royale.backtester.strategy.signal.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.backtester.strategy.signal.moving_average_strategy import (
    MovingAverageStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class MovingAverageStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Moving Average strategy.
    This strategy uses a combination of entry and exit conditions based on moving averages.
    It does not include any filter conditions or trend conditions, focusing solely on the moving average logic.
    """

    def __init__(self):
        super().__init__(
            filter_condition_types=[],
            entry_condition_types=[MovingAverageEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[MovingAverageExitCondition],
            stateful_logic_types=[],
        )
        self.strategy_class = MovingAverageStrategy
