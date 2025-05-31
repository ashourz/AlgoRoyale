import pandas as pd

from .base_strategy import Strategy


class PullbackEntryStrategy(Strategy):
    def __init__(self, ma_col: str = "sma_20", close_col: str = "close_price") -> None:
        """
        Pullback Entry Strategy:
        - Buy when price crosses above the moving average from below.
        - Sell on the next day after a buy signal.
        """
        self.ma_col = ma_col
        self.close_col = close_col

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if self.ma_col not in df.columns or self.close_col not in df.columns:
            raise ValueError(
                f"DataFrame must contain '{self.ma_col}' and '{self.close_col}' columns"
            )
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        above_ma = df[self.close_col] > df[self.ma_col]
        below_ma_yesterday = df[self.close_col].shift(1) < df[self.ma_col].shift(1)
        recovery = above_ma & below_ma_yesterday

        signals = pd.Series("hold", index=df.index, name="signal")
        signals[recovery] = "buy"
        signals[recovery.shift(-1).fillna(False)] = "sell"
        return signals
