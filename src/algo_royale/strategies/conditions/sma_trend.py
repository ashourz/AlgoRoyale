import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class SMATrendCondition(StrategyCondition):
    """
    Simple Moving Average (SMA) Trend Condition
    Checks if the fast SMA is above the slow SMA.
    Parameters:
    - sma_fast_col: Column name for the fast SMA.
    - sma_slow_col: Column name for the slow SMA.
    """

    def __init__(self, sma_fast_col, sma_slow_col):
        self.sma_fast_col = sma_fast_col
        self.sma_slow_col = sma_slow_col

    @property
    def required_columns(self):
        return {self.sma_fast_col, self.sma_slow_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.sma_fast_col] > df[self.sma_slow_col]

    def __call__(self, df):
        return self.apply(df)
