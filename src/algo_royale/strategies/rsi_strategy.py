from typing import List

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) Strategy

    Generates buy/sell signals based on RSI indicator thresholds.
    Buy when RSI is below oversold threshold, sell when above overbought.
    """

    def __init__(
        self,
        close_col: str = "close",
        period: int = 14,
        overbought: int = 70,
        oversold: int = 30,
    ) -> None:
        self.close_col = close_col
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if self.close_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {self.close_col}")
        if len(df) < self.period:
            raise ValueError(
                f"DataFrame length must be at least {self.period} for RSI calculation"
            )

        delta = df[self.close_col].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Use exponential moving average for RSI smoothing
        avg_gain = gain.ewm(com=self.period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period - 1, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))

        signals = pd.Series("hold", index=df.index, name="signal")
        signals[rsi > self.overbought] = "sell"
        signals[rsi < self.oversold] = "buy"

        return signals

    def get_required_columns(self) -> List[str]:
        """Return list of required columns for this strategy."""
        return [self.close_col]

    def get_min_data_points(self) -> int:
        """Return minimum number of data points needed to generate signals."""
        return self.period
