import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class ReturnVolatilityExitCondition(StrategyCondition):
    """
    Exit condition based on return and volatility.
    Triggers when:
    - The return is below a specified threshold, OR
    - The price range exceeds a specified volatility measure.
    """

    def __init__(
        self, return_col: str, range_col: str, volatility_col: str, threshold: float
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
