import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class VWAPReversionStrategy(Strategy):
    """
    VWAP Reversion Strategy:
    - Buy when volume-weighted price is significantly below the 20-period VWAP.
    - Sell when volume-weighted price is significantly above the 20-period VWAP.
    - Hold otherwise.

    Parameters:
    - deviation_threshold: relative deviation from VWAP to trigger buy/sell (default 0.01 = 1%)
    - vwap_col: column name for VWAP data (default "vwap_20")
    - vwp_col: column name for volume-weighted price (default "volume_weighted_price")
    """

    def __init__(
        self,
        deviation_threshold: float = 0.01,
        vwap_col: str = "vwap_20",
        vwp_col: str = "volume_weighted_price",
    ):
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell/hold signals based on deviation from VWAP.

        Parameters:
        - df: DataFrame with at least volume-weighted price and VWAP columns.

        Returns:
        - signals: pd.Series with values "buy", "sell", or "hold".
        """
        if self.vwap_col not in df.columns or self.vwp_col not in df.columns:
            raise ValueError(
                f"DataFrame must contain '{self.vwap_col}' and '{self.vwp_col}' columns."
            )

        deviation = (df[self.vwp_col] - df[self.vwap_col]) / df[self.vwap_col]

        signals = pd.Series("hold", index=df.index, name="signal")

        # Buy when price is sufficiently below VWAP (potential undervaluation)
        signals.loc[deviation < -self.deviation_threshold] = "buy"
        # Sell when price is sufficiently above VWAP (potential overvaluation)
        signals.loc[deviation > self.deviation_threshold] = "sell"

        return signals
