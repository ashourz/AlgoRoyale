import pandas as pd

from algo_royale.strategies.strategy_functions.exit.base_exit_function import (
    ExitFunction,
)


class ReturnVolatilityExit(ExitFunction):
    def __init__(
        self, return_col: str, range_col: str, volatility_col: str, threshold: float
    ):
        self.return_col = return_col
        self.range_col = range_col
        self.volatility_col = volatility_col
        self.threshold = threshold

    def __call__(self, df: pd.DataFrame) -> pd.Series:
        weakness = df[self.return_col] < self.threshold
        volatility_spike = df[self.range_col] > df[self.volatility_col]
        return weakness | volatility_spike
