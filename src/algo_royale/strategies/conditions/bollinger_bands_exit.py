import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class BollingerBandsExitCondition(StrategyCondition):
    def __init__(self, close_col="close", window=20, num_std=2):
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
