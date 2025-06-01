import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class TrendAboveSMACondition(StrategyCondition):
    def __init__(self, price_col: str, sma_col: str):
        self.price_col = price_col
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return {self.price_col, self.sma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.price_col] > df[self.sma_col]
