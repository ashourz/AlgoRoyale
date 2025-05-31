from typing import List

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MeanRevisionStrategy(Strategy):
    """
    Mean Reversion Strategy:
    - Buy when price is below a moving average by a threshold.
    - Sell when price is above a moving average by a threshold.
    - Hold otherwise.
    """

    def __init__(
        self, close_col: str = "close", window: int = 20, threshold: float = 0.02
    ):
        self.close_col = close_col
        self.window = window
        self.threshold = threshold  # e.g., 2% deviation

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ma = df[self.close_col].rolling(window=self.window, min_periods=1).mean()
        deviation = (df[self.close_col] - ma) / ma
        signals = pd.Series("hold", index=df.index)
        signals[deviation < -self.threshold] = "buy"
        signals[deviation > self.threshold] = "sell"
        return signals

    def get_required_columns(self) -> List[str]:
        return [self.close_col]

    def get_min_data_points(self) -> int:
        return self.window
