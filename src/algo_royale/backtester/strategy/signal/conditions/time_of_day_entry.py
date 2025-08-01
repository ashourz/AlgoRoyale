import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class TimeOfDayEntryCondition(StrategyCondition):
    def __init__(
        self,
        buy_start_hour=10,
        buy_end_hour=14,
        hour_col: SignalStrategyColumns = SignalStrategyColumns.HOUR,
        logger: Loggable = None,
    ):
        super().__init__(
            buy_start_hour=buy_start_hour,
            buy_end_hour=buy_end_hour,
            hour_col=hour_col,
            logger=logger,
        )
        self.buy_start_hour = buy_start_hour
        self.buy_end_hour = buy_end_hour
        self.hour_col = hour_col
        self.buy_hours = list(
            range(self.buy_start_hour, self.buy_end_hour + 1)
        )  # <-- Add this line

    @property
    def required_columns(self):
        return [self.hour_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.buy_hours)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "buy_start_hour": [8, 9, 10, 11],
            "buy_end_hour": [12, 13, 14, 15, 16],
            "hour_col": [SignalStrategyColumns.HOUR],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            buy_start_hour=trial.suggest_int(f"{prefix}buy_start_hour", 8, 11),
            buy_end_hour=trial.suggest_int(f"{prefix}buy_end_hour", 12, 16),
            hour_col=trial.suggest_categorical(
                f"{prefix}hour_col", [SignalStrategyColumns.HOUR]
            ),
        )
