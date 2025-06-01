import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class VolatilityBreakoutEntryCondition(StrategyCondition):
    """Condition to identify volatility breakout entry points in a trading strategy.
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
        breakout = (
            df[StrategyColumns.RANGE]
            > self.threshold * df[StrategyColumns.VOLATILITY_20]
        )
        # Ensure the close price is above the SMA to confirm an uptrend
        uptrend = df[StrategyColumns.CLOSE_PRICE] > df[self.sma_col]
        return breakout & uptrend
