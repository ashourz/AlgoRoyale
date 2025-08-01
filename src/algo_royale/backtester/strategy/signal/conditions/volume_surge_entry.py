import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class VolumeSurgeEntryCondition(StrategyCondition):
    def __init__(
        self,
        vol_col=SignalStrategyColumns.VOLUME,
        threshold=2.0,
        ma_window=20,
        logger: Loggable = None,
    ):
        super().__init__(
            vol_col=vol_col, threshold=threshold, ma_window=ma_window, logger=logger
        )
        self.vol_col = vol_col
        self.threshold = threshold
        self.ma_window = ma_window

    @property
    def required_columns(self):
        return [self.vol_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        vol_ma = df[self.vol_col].rolling(window=self.ma_window, min_periods=1).mean()
        surge = df[self.vol_col] > (vol_ma * self.threshold)
        return surge

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "vol_col": [SignalStrategyColumns.VOLUME],
            "threshold": [1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 4.0],
            "ma_window": [10, 20, 30, 50],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            vol_col=trial.suggest_categorical(
                f"{prefix}vol_col", [SignalStrategyColumns.VOLUME]
            ),
            threshold=trial.suggest_float(f"{prefix}threshold", 1.2, 4.0),
            ma_window=trial.suggest_int(f"{prefix}ma_window", 10, 50),
        )
