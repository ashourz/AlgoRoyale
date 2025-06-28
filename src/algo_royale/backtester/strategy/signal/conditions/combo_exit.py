import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


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
        super().__init__(
            rsi_col=rsi_col,
            macd_col=macd_col,
            volume_col=volume_col,
            vol_ma_col=vol_ma_col,
            rsi_sell_thresh=rsi_sell_thresh,
            macd_sell_thresh=macd_sell_thresh,
        )
        self.rsi_col = rsi_col
        self.macd_col = macd_col
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.rsi_sell_thresh = rsi_sell_thresh
        self.macd_sell_thresh = macd_sell_thresh

    @property
    def required_columns(self):
        return [self.rsi_col, self.macd_col, self.volume_col, self.vol_ma_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return (
            (df[self.rsi_col] > self.rsi_sell_thresh)
            & (df[self.macd_col] < self.macd_sell_thresh)
            & (df[self.volume_col] < df[self.vol_ma_col])
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
            "rsi_sell_thresh": [55, 60, 65, 70, 75, 80],
            "macd_sell_thresh": [-0.5, -0.2, -0.1, 0, 0.1],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            rsi_sell_thresh=trial.suggest_int(f"{prefix}rsi_sell_thresh", 55, 80),
            macd_sell_thresh=trial.suggest_float(
                f"{prefix}macd_sell_thresh", -0.5, 0.1
            ),
            rsi_col=trial.suggest_categorical(
                f"{prefix}rsi_col", [StrategyColumns.RSI]
            ),
            macd_col=trial.suggest_categorical(
                f"{prefix}macd_col", [StrategyColumns.MACD]
            ),
            volume_col=trial.suggest_categorical(
                f"{prefix}volume_col", [StrategyColumns.VOLUME]
            ),
            vol_ma_col=trial.suggest_categorical(
                f"{prefix}vol_ma_col",
                [
                    StrategyColumns.VOL_MA_10,
                    StrategyColumns.VOL_MA_20,
                    StrategyColumns.VOL_MA_50,
                    StrategyColumns.VOL_MA_100,
                    StrategyColumns.VOL_MA_200,
                ],
            ),
        )
