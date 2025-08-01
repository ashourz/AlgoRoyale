import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class BooleanColumnEntryCondition(StrategyCondition):
    def __init__(
        self,
        entry_col: SignalStrategyColumns = SignalStrategyColumns.ENTRY_SIGNAL,
        logger: Loggable = None,
    ):
        """
        Condition based on a boolean column.
        """
        super().__init__(entry_col=entry_col, logger=logger)
        self.entry_col = entry_col

    @property
    def required_columns(self):
        return []

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        if self.entry_col not in df.columns:
            return pd.Series(False, index=df.index)
        return df[self.entry_col].astype(bool)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "entry_col": [SignalStrategyColumns.ENTRY_SIGNAL],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            entry_col=trial.suggest_categorical(
                f"{prefix}entry_col",
                [SignalStrategyColumns.ENTRY_SIGNAL],
            ),
        )
