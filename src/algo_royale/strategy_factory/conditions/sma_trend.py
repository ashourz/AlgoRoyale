import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class SMATrendCondition(StrategyCondition):
    """
    Simple Moving Average (SMA) Trend Condition
    Checks if the fast SMA is above the slow SMA.
    Parameters:
    - sma_fast_col: Column name for the fast SMA.
    - sma_slow_col: Column name for the slow SMA.
    """

    def __init__(
        self,
        sma_fast_col: StrategyColumns = StrategyColumns.SMA_50,
        sma_slow_col: StrategyColumns = StrategyColumns.SMA_200,
    ):
        self.sma_fast_col = sma_fast_col
        self.sma_slow_col = sma_slow_col

    @property
    def required_columns(self):
        return {self.sma_fast_col, self.sma_slow_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.sma_fast_col] > df[self.sma_slow_col]

    def __call__(self, df):
        return self.apply(df)

    @classmethod
    def available_param_grid(cls):
        fast_periods = [10, 20, 50, 100]
        slow_periods = [100, 150, 200, 300]
        fast_cols = [getattr(StrategyColumns, f"SMA_{p}") for p in fast_periods]
        slow_cols = [getattr(StrategyColumns, f"SMA_{p}") for p in slow_periods]
        valid_pairs = [
            {"sma_fast_col": fast, "sma_slow_col": slow}
            for fast, fp in zip(fast_cols, fast_periods)
            for slow, sp in zip(slow_cols, slow_periods)
            if fp < sp
        ]
        return valid_pairs
