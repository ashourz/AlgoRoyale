import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class WickReversalEntryCondition(StrategyCondition):
    def __init__(
        self, wick_body_ratio=2.0, lower_wick_col="lower_wick", body_col="body"
    ):
        self.wick_body_ratio = wick_body_ratio
        self.lower_wick_col = lower_wick_col
        self.body_col = body_col

    @property
    def required_columns(self):
        return {self.lower_wick_col, self.body_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        body_safe = df[self.body_col].replace(0, 1e-8)
        long_lower_wick = df[self.lower_wick_col] > self.wick_body_ratio * body_safe
        return long_lower_wick
