import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class PullbackEntryCondition(StrategyCondition):
    def __init__(
        self,
        ma_col: StrategyColumns = StrategyColumns.SMA_20,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(ma_col=ma_col, close_col=close_col)
        self.ma_col = ma_col
        self.close_col = close_col

    @property
    def required_columns(self):
        return {self.ma_col, self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        above_ma = df[self.close_col] > df[self.ma_col]
        below_ma_yesterday = df[self.close_col].shift(1) < df[self.ma_col].shift(1)
        return above_ma & below_ma_yesterday

    @classmethod
    def available_param_grid(cls):
        return {
            "ma_col": [
                StrategyColumns.SMA_10,
                StrategyColumns.SMA_20,
                StrategyColumns.SMA_50,
                StrategyColumns.SMA_100,
                StrategyColumns.SMA_150,
                StrategyColumns.SMA_200,
                StrategyColumns.EMA_9,
                StrategyColumns.EMA_10,
                StrategyColumns.EMA_20,
                StrategyColumns.EMA_26,
                StrategyColumns.EMA_50,
                StrategyColumns.EMA_100,
                StrategyColumns.EMA_150,
                StrategyColumns.EMA_200,
            ],
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
        }
