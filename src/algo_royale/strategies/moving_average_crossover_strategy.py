from typing import List

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    """
    Moving Average Crossover Strategy:
    - Buy when the short moving average crosses above the long moving average.
    - Sell when the short moving average crosses below the long moving average.
    - Hold otherwise.
    """

    def __init__(
        self, close_col: str = "close", short_window: int = 10, long_window: int = 50
    ):
        self.close_col = close_col
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        short_ma = (
            df[self.close_col].rolling(window=self.short_window, min_periods=1).mean()
        )
        long_ma = (
            df[self.close_col].rolling(window=self.long_window, min_periods=1).mean()
        )
        signal = pd.Series(0, index=df.index)
        signal[short_ma > long_ma] = 1
        signal[short_ma < long_ma] = -1
        # Generate trading signals: buy/sell/hold
        signals = pd.Series("hold", index=df.index)
        signals[(signal == 1) & (signal.shift(1) != 1)] = "buy"
        signals[(signal == -1) & (signal.shift(1) != -1)] = "sell"
        return signals

    def get_required_columns(self) -> List[str]:
        return [self.close_col]

    def get_min_data_points(self) -> int:
        return self.long_window
