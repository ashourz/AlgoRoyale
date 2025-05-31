import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MACDStrategy(Strategy):
    """
    Moving Average Convergence Divergence (MACD) Strategy
    This strategy generates buy/sell signals based on the MACD indicator.
    It uses the closing prices of a DataFrame to calculate the MACD line and signal line,
    then generates signals based on their crossover.
    """

    def __init__(self, close_col="close", fast=12, slow=26, signal=9):
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        exp1 = df[self.close_col].ewm(span=self.fast, adjust=False).mean()
        exp2 = df[self.close_col].ewm(span=self.slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()
        signals = pd.Series("hold", index=df.index)
        signals[macd > signal_line] = "buy"
        signals[macd < signal_line] = "sell"
        return signals

    def get_required_columns(self):
        return [self.close_col]

    def get_min_data_points(self):
        return self.slow + self.signal
