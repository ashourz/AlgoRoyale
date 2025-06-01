import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class WickReversalStrategy(Strategy):
    """
    Wick Reversal Strategy:
    - Buy when the lower wick is significantly larger than the body of the candle.
    - Sell when the upper wick is significantly larger than the body of the candle.
    - Hold otherwise.

    Parameters:
    - wick_body_ratio: minimum ratio of wick to body length to trigger signals.
    """

    def __init__(
        self,
        wick_body_ratio: float = 2.0,
        upper_wick_col: str = "upper_wick",
        lower_wick_col: str = "lower_wick",
        body_col: str = "body",
    ):
        self.wick_body_ratio = wick_body_ratio
        self.upper_wick_col = upper_wick_col
        self.lower_wick_col = lower_wick_col
        self.body_col = body_col

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell/hold signals based on wick to body ratio.

        Parameters:
        - df: DataFrame containing candle anatomy columns.

        Returns:
        - signals: pd.Series with values "buy", "sell", or "hold".
        """
        required_cols = [self.upper_wick_col, self.lower_wick_col, self.body_col]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns: {required_cols}")

        # Avoid division by zero: replace zero body with a small number epsilon
        body_safe = df[self.body_col].replace(0, 1e-8)

        long_lower_wick = df[self.lower_wick_col] > self.wick_body_ratio * body_safe
        long_upper_wick = df[self.upper_wick_col] > self.wick_body_ratio * body_safe

        signals = pd.Series("hold", index=df.index, name="signal")
        signals.loc[long_lower_wick] = "buy"
        signals.loc[long_upper_wick] = "sell"

        return signals
