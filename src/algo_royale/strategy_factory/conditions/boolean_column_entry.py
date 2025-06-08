import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class BooleanColumnEntryCondition(StrategyCondition):
    def __init__(self, entry_col: StrategyColumns = StrategyColumns.ENTRY_SIGNAL):
        """
        Condition based on a boolean column.
        """
        super().__init__(entry_col=entry_col)
        self.entry_col = entry_col

    @property
    def required_columns(self):
        return {self.entry_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.entry_col].astype(bool)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "entry_col": [StrategyColumns.ENTRY_SIGNAL],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            entry_col=trial.suggest_categorical(
                f"{prefix}entry_col",
                [StrategyColumns.ENTRY_SIGNAL],
            ),
        )
