import itertools

import pandas as pd
from optuna import Trial

from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)


class VolumeSurgeExitCondition(StrategyCondition):
    def __init__(self, entry_condition: VolumeSurgeEntryCondition, debug: bool = False):
        super().__init__(entry_condition=entry_condition, debug=debug)
        self.entry_condition = entry_condition

    @property
    def required_columns(self):
        return self.entry_condition.required_columns

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        entry_mask = self.entry_condition.apply(df)
        # Sell on the next bar after a surge
        return entry_mask.shift(-1).fillna(False)

    @classmethod
    def available_param_grid(cls) -> dict:
        param_grid = VolumeSurgeEntryCondition.available_param_grid()
        thresholds = param_grid["threshold"]
        vol_cols = param_grid["vol_col"]
        ma_windows = param_grid["ma_window"]

        entry_conditions = [
            VolumeSurgeEntryCondition(
                vol_col=vol_col, threshold=threshold, ma_window=ma_window
            )
            for threshold, vol_col, ma_window in itertools.product(
                thresholds, vol_cols, ma_windows
            )
        ]
        return {"entry_condition": entry_conditions}

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            entry_condition=VolumeSurgeEntryCondition.optuna_suggest(
                trial, prefix=f"{prefix}entry_"
            )
        )
