import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TimeOfDayExitCondition(StrategyCondition):
    def __init__(
        self,
        sell_start_hour=10,
        sell_end_hour=16,
        hour_col: SignalStrategyColumns = SignalStrategyColumns.HOUR,
        debug: bool = False,
    ):
        super().__init__(
            sell_start_hour=sell_start_hour,
            sell_end_hour=sell_end_hour,
            hour_col=hour_col,
            debug=debug,
        )
        self.sell_start_hour = sell_start_hour
        self.sell_end_hour = sell_end_hour
        self.sell_hours = list(range(self.sell_start_hour, self.sell_end_hour + 1))
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return [self.hour_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.sell_hours)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "sell_start_hour": [8, 9, 10, 11],
            "sell_end_hour": [12, 13, 14, 15, 16],
            "hour_col": [SignalStrategyColumns.HOUR],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            sell_start_hour=trial.suggest_int(f"{prefix}sell_start_hour", 8, 11),
            sell_end_hour=trial.suggest_int(f"{prefix}sell_end_hour", 12, 16),
            hour_col=trial.suggest_categorical(
                f"{prefix}hour_col", [SignalStrategyColumns.HOUR]
            ),
        )
