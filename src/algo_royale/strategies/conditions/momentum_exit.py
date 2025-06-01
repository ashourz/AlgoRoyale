import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class MomentumExitCondition(StrategyCondition):
    def __init__(
        self,
        close_col="close",
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
        sell_condition = momentum < -self.threshold
        if self.confirmation_periods > 1:
            sell_confirmed = (
                sell_condition.rolling(window=self.confirmation_periods)
                .apply(lambda x: x.all(), raw=True)
                .fillna(0)
                .astype(bool)
            )
            return sell_confirmed
        return sell_condition
