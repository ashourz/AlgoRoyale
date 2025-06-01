import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class ComboEntryCondition(StrategyCondition):
    """
    Entry condition that combines RSI, MACD, and volume for buying.
    True when:
    - RSI < rsi_buy_thresh
    - MACD > macd_buy_thresh
    - Volume > vol_ma
    """

    def __init__(
        self, rsi_col, macd_col, volume_col, vol_ma_col, rsi_buy_thresh, macd_buy_thresh
    ):
        self.rsi_col = rsi_col
        self.macd_col = macd_col
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.rsi_buy_thresh = rsi_buy_thresh
        self.macd_buy_thresh = macd_buy_thresh

    @property
    def required_columns(self):
        return {self.rsi_col, self.macd_col, self.volume_col, self.vol_ma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return (
            (df[self.rsi_col] < self.rsi_buy_thresh)
            & (df[self.macd_col] > self.macd_buy_thresh)
            & (df[self.volume_col] > df[self.vol_ma_col])
        )
