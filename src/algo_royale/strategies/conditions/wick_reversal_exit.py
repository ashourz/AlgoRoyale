import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class WickReversalExitCondition(StrategyCondition):
    def __init__(
        self, wick_body_ratio=2.0, upper_wick_col="upper_wick", body_col="body"
    ):
        self.wick_body_ratio = wick_body_ratio
        self.upper_wick_col = upper_wick_col
        self.body_col = body_col

    @property
    def required_columns(self):
        return {self.upper_wick_col, self.body_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        body_safe = df[self.body_col].replace(0, 1e-8)
        long_upper_wick = df[self.upper_wick_col] > self.wick_body_ratio * body_safe
        return long_upper_wick
