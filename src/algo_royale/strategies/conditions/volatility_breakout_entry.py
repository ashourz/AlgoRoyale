import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class VolatilityBreakoutEntryCondition(StrategyCondition):
    def __init__(self, threshold=1.5, sma_col="sma_20"):
        self.threshold = threshold
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return {"volatility_20", "range", "close_price", self.sma_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        breakout = df["range"] > self.threshold * df["volatility_20"]
        uptrend = df["close_price"] > df[self.sma_col]
        return breakout & uptrend
