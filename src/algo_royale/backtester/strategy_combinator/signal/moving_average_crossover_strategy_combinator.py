from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.conditions.moving_average_crossover_entry import (
    MovingAverageCrossoverEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_crossover_exit import (
    MovingAverageCrossoverExitCondition,
)
from algo_royale.strategy_factory.strategies.moving_average_crossover_strategy import (
    MovingAverageCrossoverStrategy,
)


class MovingAverageCrossoverStrategyCombinator(SignalStrategyCombinator):
    """
    Combines conditions and logic for a Moving Average Crossover strategy.
    This strategy uses a combination of entry and exit conditions based on moving average crossovers.
    It does not include any filter conditions or trend conditions, focusing solely on the crossover logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [MovingAverageCrossoverEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [MovingAverageCrossoverExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = MovingAverageCrossoverStrategy
