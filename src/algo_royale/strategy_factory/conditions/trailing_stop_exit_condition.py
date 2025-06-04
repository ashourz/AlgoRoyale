import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TrailingStopExitCondition(StrategyCondition):
    """
    Exit when price falls below the trailing stop level.
    The trailing stop is calculated as the highest close since entry minus stop_pct.
    """

    def __init__(
        self, close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE, stop_pct=0.02
    ):
        super().__init__(close_col=close_col, stop_pct=stop_pct)
        self.close_col = close_col
        self.stop_pct = stop_pct

    def apply(self, df: pd.DataFrame) -> pd.Series:
        # Calculate the rolling maximum close (trailing high)
        trailing_high = df[self.close_col].cummax()
        trailing_stop = trailing_high * (1 - self.stop_pct)
        # Exit when price falls below trailing stop
        return df[self.close_col] < trailing_stop

    @property
    def required_columns(self):
        return {self.close_col}

    @classmethod
    def available_param_grid(cls):
        return {
            "close_col": [
                StrategyColumns.CLOSE_PRICE,
                StrategyColumns.OPEN_PRICE,
            ],
            "stop_pct": [0.01, 0.02, 0.03, 0.05],
        }
