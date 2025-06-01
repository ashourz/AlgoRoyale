import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class VWAPReversionEntryCondition(StrategyCondition):
    def __init__(
        self,
        deviation_threshold=0.01,
        vwap_col: StrategyColumns = StrategyColumns.VWAP_20,
        vwp_col: StrategyColumns = StrategyColumns.VOLUME_WEIGHTED_PRICE,
    ):
        self.deviation_threshold = deviation_threshold
        self.vwap_col = vwap_col
        self.vwp_col = vwp_col

    @property
    def required_columns(self):
        return {self.vwap_col, self.vwp_col}

    def apply(self, df: pd.DataFrame) -> pd.Series:
        deviation = (df[self.vwp_col] - df[self.vwap_col]) / df[self.vwap_col]
        return deviation < -self.deviation_threshold
