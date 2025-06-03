import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class VolumeSurgeEntryCondition(StrategyCondition):
    def __init__(self, vol_col=StrategyColumns.VOLUME, threshold=2.0, ma_window=20):
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

    @classmethod
    def available_param_grid(cls):
        return {
            "vol_col": [StrategyColumns.VOLUME],
            "threshold": [1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 4.0],
            "ma_window": [10, 20, 30, 50],
        }
