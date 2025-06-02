import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class ReturnVolatilityExitCondition(StrategyCondition):
    """
    Exit condition based on return and volatility.
    Triggers when:
    - The return is below a specified threshold, OR
    - The price range exceeds a specified volatility measure.

    """

    def __init__(
        self,
        threshold: float,
        return_col=StrategyColumns.PCT_RETURN,  # or LOG_RETURN
        range_col: StrategyColumns = StrategyColumns.RANGE,
        volatility_col: StrategyColumns = StrategyColumns.VOLATILITY_20,
    ):
        self.return_col = return_col
        self.range_col = range_col
        self.volatility_col = volatility_col
        self.threshold = threshold

    @property
    def required_columns(self):
        return {self.return_col, self.range_col, self.volatility_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        weakness = df[self.return_col] < self.threshold
        volatility_spike = df[self.range_col] > df[self.volatility_col]
        return weakness | volatility_spike

    @classmethod
    def available_param_grid(cls):
        return {
            "threshold": [-0.005, -0.01, -0.02, -0.03, -0.04, -0.05, -0.06, -0.1],
            "return_col": [
                StrategyColumns.PCT_RETURN,
                StrategyColumns.LOG_RETURN,
            ],
            "range_col": [StrategyColumns.RANGE],
            "volatility_col": [
                StrategyColumns.HIST_VOLATILITY_20,
                StrategyColumns.VOLATILITY_10,
                StrategyColumns.VOLATILITY_20,
                StrategyColumns.VOLATILITY_50,
            ],
        }
