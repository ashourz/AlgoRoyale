import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class VolumeSurgeEntryCondition(StrategyCondition):
    def __init__(self, vol_col="volume", threshold=2.0, ma_window=20):
        self.vol_col = vol_col
        self.threshold = threshold
        self.ma_window = ma_window

    @property
    def required_columns(self):
        return {self.vol_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        vol_ma = df[self.vol_col].rolling(window=self.ma_window, min_periods=1).mean()
        surge = df[self.vol_col] > (vol_ma * self.threshold)
        return surge
