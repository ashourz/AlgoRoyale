import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class ComboStrategy(Strategy):
    """
    Combo Strategy:
    - Buy when RSI < 30, MACD > 0, and volume > 20-day MA volume.
    - Sell when RSI > 70, MACD < 0, and volume < 20-day MA volume.
    - Hold otherwise.
    """

    def __init__(
        self,
        rsi_col="rsi",
        macd_col="macd",
        volume_col="volume",
        vol_ma_col="vol_ma_20",
        rsi_buy_thresh=30,
        rsi_sell_thresh=70,
        macd_buy_thresh=0,
        macd_sell_thresh=0,
    ):
        self.rsi_col = rsi_col
        self.macd_col = macd_col
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.rsi_buy_thresh = rsi_buy_thresh
        self.rsi_sell_thresh = rsi_sell_thresh
        self.macd_buy_thresh = macd_buy_thresh
        self.macd_sell_thresh = macd_sell_thresh

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        # Buy condition
        buy_cond = (
            (df[self.rsi_col] < self.rsi_buy_thresh)
            & (df[self.macd_col] > self.macd_buy_thresh)
            & (df[self.volume_col] > df[self.vol_ma_col])
        )

        # Sell condition
        sell_cond = (
            (df[self.rsi_col] > self.rsi_sell_thresh)
            & (df[self.macd_col] < self.macd_sell_thresh)
            & (df[self.volume_col] < df[self.vol_ma_col])
        )

        signals[buy_cond] = "buy"
        signals[sell_cond] = "sell"
        # Others remain "hold"

        return signals
