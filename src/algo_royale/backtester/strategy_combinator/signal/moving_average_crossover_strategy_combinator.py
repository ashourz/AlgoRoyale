from algo_royale.backtester.strategy.signal.conditions.moving_average_crossover_entry import (
    MovingAverageCrossoverEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_crossover_exit import (
    MovingAverageCrossoverExitCondition,
)
from algo_royale.backtester.strategy.signal.moving_average_crossover_strategy import (
    MovingAverageCrossoverStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class MovingAverageCrossoverStrategyCombinator(SignalStrategyCombinator):
    """
    Combines conditions and logic for a Moving Average Crossover strategy.
    This strategy uses a combination of entry and exit conditions based on moving average crossovers.
    It does not include any filter conditions or trend conditions, focusing solely on the crossover logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=MovingAverageCrossoverStrategy,
            filter_condition_types=[],
            entry_condition_types=[MovingAverageCrossoverEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[MovingAverageCrossoverExitCondition],
            stateful_logic_types=[],
        )
