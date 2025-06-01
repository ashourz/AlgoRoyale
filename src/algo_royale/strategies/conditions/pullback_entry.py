import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class PullbackEntryCondition(StrategyCondition):
    def __init__(self, ma_col="sma_20", close_col="close_price"):
        self.ma_col = ma_col
        self.close_col = close_col

    @property
    def required_columns(self):
        return {self.ma_col, self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        above_ma = df[self.close_col] > df[self.ma_col]
        below_ma_yesterday = df[self.close_col].shift(1) < df[self.ma_col].shift(1)
        return above_ma & below_ma_yesterday
