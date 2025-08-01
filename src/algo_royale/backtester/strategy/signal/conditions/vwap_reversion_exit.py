import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class VWAPReversionExitCondition(StrategyCondition):
    def __init__(
        self,
        deviation_threshold=0.01,
        vwap_col: SignalStrategyColumns = SignalStrategyColumns.VWAP_20,
        vwp_col: SignalStrategyColumns = SignalStrategyColumns.VOLUME_WEIGHTED_PRICE,
        logger: Loggable = None,
    ):
        super().__init__(
            deviation_threshold=deviation_threshold,
            vwap_col=vwap_col,
            vwp_col=vwp_col,
            logger=logger,
        )
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

    @property
    def required_columns(self):
        return [self.vwap_col, self.vwp_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        deviation = (df[self.vwp_col] - df[self.vwap_col]) / df[self.vwap_col]
        return deviation > self.deviation_threshold

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "deviation_threshold": [0.005, 0.01, 0.015, 0.02],
            "vwap_col": [
                SignalStrategyColumns.VWAP_10,
                SignalStrategyColumns.VWAP_20,
                SignalStrategyColumns.VWAP_50,
                SignalStrategyColumns.VWAP_100,
                SignalStrategyColumns.VWAP_150,
                SignalStrategyColumns.VWAP_200,
            ],
            "vwp_col": [SignalStrategyColumns.VOLUME_WEIGHTED_PRICE],
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
                    SignalStrategyColumns.VWAP_10,
                    SignalStrategyColumns.VWAP_20,
                    SignalStrategyColumns.VWAP_50,
                    SignalStrategyColumns.VWAP_100,
                    SignalStrategyColumns.VWAP_150,
                    SignalStrategyColumns.VWAP_200,
                ],
            ),
            vwp_col=trial.suggest_categorical(
                f"{prefix}vwp_col", [SignalStrategyColumns.VOLUME_WEIGHTED_PRICE]
            ),
        )
