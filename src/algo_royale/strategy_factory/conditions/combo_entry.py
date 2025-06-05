import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class ComboEntryCondition(StrategyCondition):
    """
    Entry condition that combines RSI, MACD, and volume for buying.
    True when:
    - RSI < rsi_buy_thresh
    - MACD > macd_buy_thresh
    - Volume > vol_ma
    """

    def __init__(
        self,
        rsi_buy_thresh,
        macd_buy_thresh,
        rsi_col: StrategyColumns = StrategyColumns.RSI,
        macd_col: StrategyColumns = StrategyColumns.MACD,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        vol_ma_col: StrategyColumns = StrategyColumns.VOL_MA_20,
    ):
        super().__init__(
            rsi_col=rsi_col,
            macd_col=macd_col,
            volume_col=volume_col,
            vol_ma_col=vol_ma_col,
            rsi_buy_thresh=rsi_buy_thresh,
            macd_buy_thresh=macd_buy_thresh,
        )
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

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "rsi_col": [StrategyColumns.RSI],
            "macd_col": [StrategyColumns.MACD],
            "volume_col": [StrategyColumns.VOLUME],
            "vol_ma_col": [
                StrategyColumns.VOL_MA_10,
                StrategyColumns.VOL_MA_20,
                StrategyColumns.VOL_MA_50,
                StrategyColumns.VOL_MA_100,
                StrategyColumns.VOL_MA_200,
            ],
            "rsi_buy_thresh": [20, 30, 35, 40, 45, 50],
            "macd_buy_thresh": [-0.1, 0, 0.1, 0.2, 0.5],
        }
