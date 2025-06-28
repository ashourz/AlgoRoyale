from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.strategy_factory.strategies.base_signal_strategy import (
    BaseSignalStrategy,
)


class MovingAverageStrategy(BaseSignalStrategy):
    """Combines conditions and logic for a Moving Average strategy.
    This strategy uses a combination of entry and exit conditions based on moving averages.
    It does not include any filter conditions or trend conditions, focusing solely on the moving average logic.
    """

    def __init__(
        self,
        entry_conditions: list[MovingAverageEntryCondition] = [
            MovingAverageEntryCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                short_window=50,
                long_window=200,
            )
        ],
        exit_conditions: list[MovingAverageExitCondition] = [
            MovingAverageExitCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                short_window=50,
                long_window=200,
            )
        ],
    ):
        """Initialize the Moving Average Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        """
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
