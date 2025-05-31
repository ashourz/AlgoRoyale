import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Strategy
    This strategy generates buy/sell signals based on Bollinger Bands.
    It uses the closing prices of a DataFrame to calculate the upper and lower bands,
    then generates signals based on price movements relative to these bands.
    """

    def __init__(self, close_col="close", window=20, num_std=2):
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        rolling_mean = df[self.close_col].rolling(window=self.window).mean()
        rolling_std = df[self.close_col].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        signals = pd.Series("hold", index=df.index)
        signals[df[self.close_col] > upper_band] = "sell"
        signals[df[self.close_col] < lower_band] = "buy"
        return signals

    def get_required_columns(self):
        return [self.close_col]

    def get_min_data_points(self):
        return self.window
