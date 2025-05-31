import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class VWAPReversionStrategy(Strategy):
    def __init__(self, deviation_threshold: float = 0.01):
        self.deviation_threshold = deviation_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        if "volume_weighted_price" not in df.columns or "vwap_20" not in df.columns:
            raise ValueError("Missing required VWAP columns")

        deviation = (df["volume_weighted_price"] - df["vwap_20"]) / df["vwap_20"]

        signals[deviation < -self.deviation_threshold] = "buy"
        signals[deviation > self.deviation_threshold] = "sell"

        return signals
