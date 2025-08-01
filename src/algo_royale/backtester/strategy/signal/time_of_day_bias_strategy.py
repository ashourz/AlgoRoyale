from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.time_of_day_entry import (
    TimeOfDayEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.time_of_day_exit import (
    TimeOfDayExitCondition,
)
from algo_royale.logging.loggable import Loggable
from src.algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class TimeOfDayBiasStrategy(BaseSignalStrategy):
    """
    Time of Day Bias Strategy:
    - Buy at specific hours of the day.
    - Sell at specific hours of the day.
    - Hold otherwise.
    Assumes DataFrame has an 'hour' column with integer hour values (0-23).
    """

    def __init__(
        self,
        logger: Loggable,
        entry_conditions: list[TimeOfDayEntryCondition] = [
            TimeOfDayEntryCondition(
                buy_start_hour=10, buy_end_hour=14, hour_col=SignalStrategyColumns.HOUR
            )
        ],
        exit_conditions: list[TimeOfDayExitCondition] = [
            TimeOfDayExitCondition(
                sell_start_hour=11,
                sell_end_hour=15,
                hour_col=SignalStrategyColumns.HOUR,
            )
        ],
    ):
        """Initialize the Time of Day Bias Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            logger=logger,
        )
