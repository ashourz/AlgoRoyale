import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class BooleanColumnEntryCondition(StrategyCondition):
    def __init__(self, entry_col: StrategyColumns = StrategyColumns.ENTRY_SIGNAL):
        """
        Condition based on a boolean column.
        """
        self.entry_col = entry_col

    @property
    def required_columns(self):
        return {self.entry_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.entry_col].astype(bool)

    @classmethod
    def available_param_grid(cls):
        return {
            "entry_col": [StrategyColumns.ENTRY_SIGNAL],
        }
