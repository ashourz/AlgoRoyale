import pandas as pd

from .base_strategy import Strategy


class TimeOfDayBiasStrategy(Strategy):
    """
    Time of Day Bias Strategy:
    - Buy at specific hours of the day.
    - Sell at specific hours of the day.
    - Hold otherwise.

    Assumes DataFrame has an 'hour' column with integer hour values (0-23).
    """

    def __init__(self, buy_hours={10, 14}, sell_hours={11, 15}, hour_col="hour"):
        self.buy_hours = buy_hours
        self.sell_hours = sell_hours
        self.hour_col = hour_col

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        if self.hour_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {self.hour_col}")

        signals = pd.Series("hold", index=df.index, name="signal")
        signals[df[self.hour_col].isin(self.buy_hours)] = "buy"
        signals[df[self.hour_col].isin(self.sell_hours)] = "sell"
        return signals
