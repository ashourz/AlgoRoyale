import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class VolatilityBreakoutExitCondition(StrategyCondition):
    """Condition to identify volatility breakout exit points in a trading strategy.
    This condition checks if the price range exceeds a specified threshold relative to the 20-period volatility,"""

    def __init__(
        self, threshold=1.5, sma_col: StrategyColumns = StrategyColumns.SMA_20
    ):
        self.threshold = threshold
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return {
            StrategyColumns.VOLATILITY_20,
            StrategyColumns.RANGE,
            StrategyColumns.CLOSE_PRICE,
            self.sma_col,
        }

    def apply(self, df: pd.DataFrame) -> pd.Series:
        breakout = df[StrategyColumns.RANGE] > self.threshold * df[StrategyColumns]
        downtrend = df[StrategyColumns.CLOSE_PRICE] <= df[self.sma_col]
        return breakout & downtrend

    @classmethod
    def available_param_grid(cls):
        return {
            "threshold": [0.8, 1.0, 1.2, 1.5, 2.0, 2.5],
            "sma_col": [
                StrategyColumns.SMA_10,
                StrategyColumns.SMA_20,
                StrategyColumns.SMA_50,
                StrategyColumns.SMA_100,
                StrategyColumns.SMA_150,
                StrategyColumns.SMA_200,
            ],
        }
