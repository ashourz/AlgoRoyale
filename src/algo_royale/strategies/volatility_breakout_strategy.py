import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class VolatilityBreakoutStrategy(Strategy):
    """
    Volatility Breakout Strategy:
    - Buy when price breaks above a volatility threshold and is above SMA.
    - Sell when price breaks above volatility threshold but is below SMA.
    - Hold otherwise.

    Parameters:
    - threshold: multiplier for volatility_20 to define breakout level.
    - sma_col: column name for moving average, default "sma_20".
    """

    def __init__(self, threshold: float = 1.5, sma_col: str = "sma_20"):
        self.threshold = threshold
        self.sma_col = sma_col

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        required_cols = ["volatility_20", "range", "close_price", self.sma_col]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Optional: handle NaNs
        df = df.dropna(subset=required_cols)

        breakout = df["range"] > self.threshold * df["volatility_20"]
        uptrend = df["close_price"] > df[self.sma_col]

        signals.loc[breakout & uptrend] = "buy"
        signals.loc[breakout & (~uptrend)] = "sell"

        return signals
