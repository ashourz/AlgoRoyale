import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class MovingAverageEntryCondition(StrategyCondition):
    """
    Entry condition based on a moving average crossover strategy.
    This condition generates a signal when a short-term moving average crosses above
    a long-term moving average, indicating a potential bullish trend.
    Args:
        close_col (str): Column name for the close price.
        short_window (int): Window size for the short moving average.
        long_window (int): Window size for the long moving average.
    Returns:
        pd.Series: Boolean Series where True indicates a buy signal based on the moving average crossover.
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        short_long_window: tuple[int, int] = (50, 200),
    ):
        self.close_col = close_col
        self.short_window, self.long_window = short_long_window

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        short_ma = (
            df[self.close_col]
            .rolling(window=self.short_window, min_periods=self.short_window)
            .mean()
        )
        long_ma = (
            df[self.close_col]
            .rolling(window=self.long_window, min_periods=self.long_window)
            .mean()
        )
        # Golden Cross: short_ma crosses above long_ma
        signal_state = pd.Series(0, index=df.index)
        signal_state.loc[short_ma > long_ma] = 1
        signal_state.loc[short_ma < long_ma] = -1
        golden_cross = (signal_state == 1) & (signal_state.shift(1) != 1)
        return golden_cross

    @classmethod
    def available_param_grid(cls):
        short_windows = [5, 10, 15, 20, 50]
        long_windows = [30, 50, 100, 200]
        valid_pairs = [
            (short, long)
            for short in short_windows
            for long in long_windows
            if short < long
        ]
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE],
            "short_long_window": valid_pairs,
        }
