import pandas as pd

from algo_royale.strategies.strategy_functions.trend.base_trend_function import (
    TrendFunction,
)


class EMAAboveSMARollingTrend(TrendFunction):
    def __init__(self, ema_col: str, sma_col: str, window: int = 3):
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.window = window

    @property
    def required_columns(self):
        return {self.ema_col, self.sma_col}

    def __call__(self, df: pd.DataFrame) -> pd.Series:
        trend = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        return trend.rolling(window=self.window).sum() == self.window
