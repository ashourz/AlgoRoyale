import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class WickReversalExitCondition(StrategyCondition):
    def __init__(
        self,
        wick_body_ratio=2.0,
        upper_wick_col=SignalStrategyColumns.UPPER_WICK,
        body_col=SignalStrategyColumns.BODY,
    ):
        super().__init__(
            wick_body_ratio=wick_body_ratio,
            upper_wick_col=upper_wick_col,
            body_col=body_col,
        )
        self.wick_body_ratio = wick_body_ratio
        self.upper_wick_col = upper_wick_col
        self.body_col = body_col

    @property
    def required_columns(self):
        return [self.upper_wick_col, self.body_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        body_safe = df[self.body_col].replace(0, 1e-8)
        long_upper_wick = df[self.upper_wick_col] > self.wick_body_ratio * body_safe
        return long_upper_wick

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "wick_body_ratio": [1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 3.0, 4.0],
            "upper_wick_col": [SignalStrategyColumns.UPPER_WICK],
            "body_col": [SignalStrategyColumns.BODY],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            wick_body_ratio=trial.suggest_float(f"{prefix}wick_body_ratio", 1.2, 4.0),
            upper_wick_col=trial.suggest_categorical(
                f"{prefix}upper_wick_col", [SignalStrategyColumns.UPPER_WICK]
            ),
            body_col=trial.suggest_categorical(
                f"{prefix}body_col", [SignalStrategyColumns.BODY]
            ),
        )
