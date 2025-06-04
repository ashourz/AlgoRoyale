import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class MomentumEntryCondition(StrategyCondition):
    def __init__(
        self,
        close_col=StrategyColumns.CLOSE_PRICE,
        lookback=10,
        threshold=0.0,
        smooth_window=None,
        confirmation_periods=1,
    ):
        self.close_col = close_col
        self.lookback = lookback
        self.threshold = threshold
        self.smooth_window = smooth_window
        self.confirmation_periods = confirmation_periods

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        momentum = df[self.close_col].pct_change(periods=self.lookback)
        if self.smooth_window:
            momentum = momentum.rolling(window=self.smooth_window, min_periods=1).mean()
        buy_condition = momentum > self.threshold
        if self.confirmation_periods > 1:
            buy_confirmed = (
                buy_condition.rolling(window=self.confirmation_periods)
                .apply(lambda x: x.all(), raw=True)
                .fillna(0)
                .astype(bool)
            )
            return buy_confirmed
        return buy_condition

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "lookback": [2, 3, 5, 10, 15, 20, 30],
            "threshold": [0.005, 0.01, 0.02, 0.03, 0.05],
            "smooth_window": [None, 3, 5, 10],
            "confirmation_periods": [1, 2, 3, 4, 5],
        }
