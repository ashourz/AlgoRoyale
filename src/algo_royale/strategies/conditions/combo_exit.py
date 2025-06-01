import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class ComboExitCondition(StrategyCondition):
    """
    Exit condition that combines RSI, MACD, and volume for selling.
    True when:
    - RSI > rsi_sell_thresh
    - MACD < macd_sell_thresh
    - Volume < vol_ma
    """

    def __init__(
        self,
        rsi_sell_thresh,
        macd_sell_thresh,
        rsi_col: StrategyColumns = StrategyColumns.RSI,
        macd_col: StrategyColumns = StrategyColumns.MACD,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        vol_ma_col: StrategyColumns = StrategyColumns.VOL_MA_20,
    ):
        self.rsi_col = rsi_col
        self.macd_col = macd_col
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.rsi_sell_thresh = rsi_sell_thresh
        self.macd_sell_thresh = macd_sell_thresh

    @property
    def required_columns(self):
        return {self.rsi_col, self.macd_col, self.volume_col, self.vol_ma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return (
            (df[self.rsi_col] > self.rsi_sell_thresh)
            & (df[self.macd_col] < self.macd_sell_thresh)
            & (df[self.volume_col] < df[self.vol_ma_col])
        )
