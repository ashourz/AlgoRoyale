import pandas as pd

from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.strategy_factory.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)


class VolumeSurgeExitCondition(StrategyCondition):
    def __init__(self, entry_condition: VolumeSurgeEntryCondition):
        self.entry_condition = entry_condition

    @property
    def required_columns(self):
        return self.entry_condition.required_columns

    def apply(self, df: pd.DataFrame) -> pd.Series:
        entry_mask = self.entry_condition.apply(df)
        # Sell on the next bar after a surge
        return entry_mask.shift(-1).fillna(False)
