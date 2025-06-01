import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class EMAAboveSMARollingCondition(StrategyCondition):
    """
    Condition that checks if the EMA is above the SMA and rising for a rolling window.
    True when EMA > SMA and EMA is increasing for the specified window.
    """

    def __init__(
        self,
        ema_col: StrategyColumns = StrategyColumns.EMA_20,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
        window: int = 3,
    ):
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.window = window

    @property
    def required_columns(self):
        return {self.ema_col, self.sma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        trend = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        return trend.rolling(window=self.window).sum() == self.window
