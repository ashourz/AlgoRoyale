import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class TimeOfDayExitCondition(StrategyCondition):
    def __init__(self, sell_hours={11, 15}, hour_col="hour"):
        self.sell_hours = set(sell_hours)
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return {self.hour_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.sell_hours)
