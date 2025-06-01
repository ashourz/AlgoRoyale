from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.time_of_day_entry import TimeOfDayEntryCondition
from algo_royale.strategies.conditions.time_of_day_exit import TimeOfDayExitCondition

from .base_strategy import Strategy


class TimeOfDayBiasStrategy(Strategy):
    """
    Time of Day Bias Strategy:
    - Buy at specific hours of the day.
    - Sell at specific hours of the day.
    - Hold otherwise.
    Assumes DataFrame has an 'hour' column with integer hour values (0-23).
    """

    def __init__(
        self, buy_hours={10, 14}, sell_hours={11, 15}, hour_col=StrategyColumns.HOUR
    ):
        self.buy_hours = buy_hours
        self.sell_hours = sell_hours
        self.hour_col = hour_col

        self.entry_conditions = [
            TimeOfDayEntryCondition(buy_hours=buy_hours, hour_col=hour_col)
        ]
        self.exit_conditions = [
            TimeOfDayExitCondition(sell_hours=sell_hours, hour_col=hour_col)
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
