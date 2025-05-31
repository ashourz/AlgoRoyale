from typing import List

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MomentumStrategy(Strategy):
    """
    Simple momentum strategy:
    - Buy if the return over the lookback period is positive,
    - Sell if negative,
    - Hold otherwise.
    """

    def __init__(self, close_col: str = "close", lookback: int = 10):
        self.close_col = close_col
        self.lookback = lookback

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Calculate momentum as the difference between current and lookback close
        momentum = df[self.close_col] - df[self.close_col].shift(self.lookback)
        signals = pd.Series("hold", index=df.index)
        signals[momentum > 0] = "buy"
        signals[momentum < 0] = "sell"
        return signals

    def get_required_columns(self) -> List[str]:
        return [self.close_col]

    def get_min_data_points(self) -> int:
        return self.lookback + 1
