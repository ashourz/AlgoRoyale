from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.strategy_factory.strategies.moving_average_strategy import (
    MovingAverageStrategy,
)


class MovingAverageStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Moving Average strategy.
    This strategy uses a combination of entry and exit conditions based on moving averages.
    It does not include any filter conditions or trend conditions, focusing solely on the moving average logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [MovingAverageEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [MovingAverageExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = MovingAverageStrategy
