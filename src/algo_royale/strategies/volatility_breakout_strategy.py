import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class VolatilityBreakoutStrategy(Strategy):
    """Volatility Breakout Strategy:
    - Buy when the price breaks out above a certain threshold of volatility.
    - Sell when the price breaks down below a certain threshold of volatility.
    - Hold otherwise.
    """

    def __init__(self, threshold: float = 1.5):
        self.threshold = threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        if "volatility_20" not in df.columns or "range" not in df.columns:
            raise ValueError(
                "DataFrame must contain 'volatility_20' and 'range' columns."
            )

        breakout = df["range"] > self.threshold * df["volatility_20"]
        uptrend = df["close_price"] > df["sma_20"]

        signals[breakout & uptrend] = "buy"
        signals[breakout & (~uptrend)] = "sell"

        return signals
