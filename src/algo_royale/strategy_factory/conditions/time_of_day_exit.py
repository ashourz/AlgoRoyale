import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TimeOfDayExitCondition(StrategyCondition):
    def __init__(
        self, sell_hours={11, 15}, hour_col: StrategyColumns = StrategyColumns.HOUR
    ):
        super().__init__(sell_hours=sell_hours, hour_col=hour_col)
        self.sell_hours = set(sell_hours)
        self.hour_col = hour_col

    @property
    def required_columns(self):
        return {self.hour_col}

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.hour_col].isin(self.sell_hours)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "sell_hours": [
                {11, 15},
                {10, 12, 14},
                {9, 13, 16},
                {8, 10, 12, 14},
            ],
            "hour_col": [StrategyColumns.HOUR],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        sell_hours = {
            hour
            for hour in range(8, 17)
            if trial.suggest_categorical(f"{prefix}hour_{hour}", [True, False])
        }

        if not sell_hours:
            # Ensure at least one hour is selected (fallback or resample logic)
            sell_hours.add(trial.suggest_int(f"{prefix}fallback_hour", 8, 16))

        return cls(
            sell_hours=sell_hours,
            hour_col=trial.suggest_categorical(
                f"{prefix}hour_col", [StrategyColumns.HOUR]
            ),
        )
