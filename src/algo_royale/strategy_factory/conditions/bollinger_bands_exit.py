import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class BollingerBandsExitCondition(StrategyCondition):
    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        window=20,
        num_std=2,
    ):
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        rolling_mean = df[self.close_col].rolling(window=self.window).mean()
        rolling_std = df[self.close_col].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        valid_idx = rolling_mean.notna()
        return valid_idx & (df[self.close_col] > upper_band)

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE],
            "window": [10, 20, 30],
            "num_std": [1, 2, 3],
        }
