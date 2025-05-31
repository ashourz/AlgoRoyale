import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) Strategy
    This strategy generates buy/sell signals based on the RSI indicator.
    It uses the closing prices of a DataFrame to calculate the RSI,
    then generates signals based on overbought and oversold thresholds.
    """

    def __init__(self, close_col="close", period=14, overbought=70, oversold=30):
        self.close_col = close_col
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        delta = df[self.close_col].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.period, min_periods=1).mean()
        avg_loss = loss.rolling(self.period, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        signals = pd.Series("hold", index=df.index)
        signals[rsi > self.overbought] = "sell"
        signals[rsi < self.oversold] = "buy"
        return signals

    def get_required_columns(self):
        return [self.close_col]

    def get_min_data_points(self):
        return self.period
