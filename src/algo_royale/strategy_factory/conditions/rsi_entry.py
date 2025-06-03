import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class RSIEntryCondition(StrategyCondition):
    def __init__(self, close_col=StrategyColumns.CLOSE_PRICE, period=14, oversold=30):
        self.close_col = close_col
        self.period = period
        self.oversold = oversold

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        delta = df[self.close_col].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=self.period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi < self.oversold

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE],
            "period": [5, 10, 14, 20, 30],
            "oversold": [20, 25, 30, 35, 40],
        }
