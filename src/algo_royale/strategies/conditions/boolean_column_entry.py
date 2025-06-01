import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class BooleanColumnEntryCondition(StrategyCondition):
    def __init__(self, entry_col: str):
        self.entry_col = entry_col

    @property
    def required_columns(self):
        return {self.entry_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.entry_col].astype(bool)
