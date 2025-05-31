import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class WickReversalStrategy(Strategy):
    def __init__(self, wick_body_ratio: float = 2.0):
        self.wick_body_ratio = wick_body_ratio

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        if not all(col in df.columns for col in ["upper_wick", "lower_wick", "body"]):
            raise ValueError("Missing candle anatomy columns.")

        long_lower_wick = df["lower_wick"] > self.wick_body_ratio * df["body"]
        long_upper_wick = df["upper_wick"] > self.wick_body_ratio * df["body"]

        signals[long_lower_wick] = "buy"
        signals[long_upper_wick] = "sell"

        return signals
