import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class WickReversalEntryCondition(StrategyCondition):
    def __init__(
        self,
        wick_body_ratio=2.0,
        lower_wick_col: StrategyColumns = StrategyColumns.LOWER_WICK,
        body_col: StrategyColumns = StrategyColumns.BODY,
    ):
        super().__init__(
            wick_body_ratio=wick_body_ratio,
            lower_wick_col=lower_wick_col,
            body_col=body_col,
        )
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

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "wick_body_ratio": [1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 3.0, 4.0],
            "lower_wick_col": [StrategyColumns.LOWER_WICK],
            "body_col": [StrategyColumns.BODY],
        }
