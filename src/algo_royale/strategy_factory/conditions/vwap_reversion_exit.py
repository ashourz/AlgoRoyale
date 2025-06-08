import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class VWAPReversionExitCondition(StrategyCondition):
    def __init__(
        self,
        deviation_threshold=0.01,
        vwap_col: StrategyColumns = StrategyColumns.VWAP_20,
        vwp_col: StrategyColumns = StrategyColumns.VOLUME_WEIGHTED_PRICE,
    ):
        super().__init__(
            deviation_threshold=deviation_threshold,
            vwap_col=vwap_col,
            vwp_col=vwp_col,
        )
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

    @property
    def required_columns(self):
        return {self.vwap_col, self.vwp_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        deviation = (df[self.vwp_col] - df[self.vwap_col]) / df[self.vwap_col]
        return deviation > self.deviation_threshold

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "deviation_threshold": [0.005, 0.01, 0.015, 0.02],
            "vwap_col": [
                StrategyColumns.VWAP_10,
                StrategyColumns.VWAP_20,
                StrategyColumns.VWAP_50,
                StrategyColumns.VWAP_100,
                StrategyColumns.VWAP_150,
                StrategyColumns.VWAP_200,
            ],
            "vwp_col": [StrategyColumns.VOLUME_WEIGHTED_PRICE],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            deviation_threshold=trial.suggest_float(
                f"{prefix}deviation_threshold", 0.005, 0.02
            ),
            vwap_col=trial.suggest_categorical(
                f"{prefix}vwap_col",
                [
                    StrategyColumns.VWAP_10,
                    StrategyColumns.VWAP_20,
                    StrategyColumns.VWAP_50,
                    StrategyColumns.VWAP_100,
                    StrategyColumns.VWAP_150,
                    StrategyColumns.VWAP_200,
                ],
            ),
            vwp_col=trial.suggest_categorical(
                f"{prefix}vwp_col", [StrategyColumns.VOLUME_WEIGHTED_PRICE]
            ),
        )
