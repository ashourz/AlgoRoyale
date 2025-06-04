import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TimeOfDayEntryCondition(StrategyCondition):
    def __init__(
        self, buy_hours={10, 14}, hour_col: StrategyColumns = StrategyColumns.HOUR
    ):
        super().__init__(buy_hours=buy_hours, hour_col=hour_col)
        self.buy_hours = set(buy_hours)
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return {self.hour_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.buy_hours)

    @classmethod
    def available_param_grid(cls):
        return {
            "buy_hours": [
                {10, 14},
                {9, 12, 15},
                {11, 13, 16},
                {8, 10, 12, 14},
            ],
            "hour_col": [StrategyColumns.HOUR],
        }
