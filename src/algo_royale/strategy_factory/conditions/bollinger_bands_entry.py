import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class BollingerBandsEntryCondition(StrategyCondition):
    """
    Condition based on Bollinger Bands.
    True when price is below lower band or above upper band.
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        window=20,
        num_std=2,
    ):
        super().__init__(close_col=close_col, window=window, num_std=num_std)
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    @property
    def required_columns(self):
        return {self.close_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        rolling_mean = df[self.close_col].rolling(window=self.window).mean()
        rolling_std = df[self.close_col].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        valid_idx = rolling_mean.notna()
        condition = pd.Series(False, index=df.index)
        condition[
            valid_idx
            & ((df[self.close_col] < lower_band) | (df[self.close_col] > upper_band))
        ] = True
        return condition

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "window": [10, 20, 30],
            "num_std": [1, 2, 3],
        }
