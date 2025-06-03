import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TimeOfDayExitCondition(StrategyCondition):
    def __init__(
        self, sell_hours={11, 15}, hour_col: StrategyColumns = StrategyColumns.HOUR
    ):
        self.sell_hours = set(sell_hours)
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return {self.hour_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.sell_hours)

    @classmethod
    def available_param_grid(cls):
        return {
            "sell_hours": [
                {11, 15},
                {10, 12, 14},
                {9, 13, 16},
                {8, 10, 12, 14},
            ],
            "hour_col": [StrategyColumns.HOUR],
        }
