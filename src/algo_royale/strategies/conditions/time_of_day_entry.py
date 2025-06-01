import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class TimeOfDayEntryCondition(StrategyCondition):
    def __init__(self, buy_hours={10, 14}, hour_col="hour"):
        self.buy_hours = set(buy_hours)
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return {self.hour_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.buy_hours)
