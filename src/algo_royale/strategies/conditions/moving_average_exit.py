import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class MovingAverageExitCondition(StrategyCondition):
    """
    Moving Average Exit Condition
    This condition checks for a Death Cross, where a short-term moving average crosses below a long-term moving average.
    Args:
        close_col (str): Column name for the close price.
        short_window (int): Window size for the short moving average.
        long_window (int): Window size for the long moving average.
    Returns:
        pd.Series: Boolean Series where True indicates a sell signal based on the moving average crossover.
    """

    def __init__(self, close_col="close", short_window=50, long_window=200):
        self.close_col = close_col
        self.short_window = short_window
        self.long_window = long_window

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        short_ma = (
            df[self.close_col].rolling(window=self.short_window, min_periods=1).mean()
        )
        long_ma = (
            df[self.close_col].rolling(window=self.long_window, min_periods=1).mean()
        )
        # Death Cross: short_ma crosses below long_ma
        signal_state = pd.Series(0, index=df.index)
        signal_state.loc[short_ma > long_ma] = 1
        signal_state.loc[short_ma < long_ma] = -1
        death_cross = (signal_state == -1) & (signal_state.shift(1) != -1)
        return death_cross
