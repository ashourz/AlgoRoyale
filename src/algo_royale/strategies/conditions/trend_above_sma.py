import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class TrendAboveSMACondition(StrategyCondition):
    def __init__(
        self,
        price_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
    ):
        self.price_col = price_col
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return {self.price_col, self.sma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.price_col] > df[self.sma_col]
