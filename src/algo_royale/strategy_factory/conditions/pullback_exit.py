import pandas as pd

from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.strategy_factory.conditions.pullback_entry import (
    PullbackEntryCondition,
)


class PullbackExitCondition(StrategyCondition):
    def __init__(self, entry_condition: PullbackEntryCondition):
        self.entry_condition = entry_condition

    @property
    def required_columns(self):
        return self.entry_condition.required_columns

    def apply(self, df: pd.DataFrame) -> pd.Series:
        entry_mask = self.entry_condition.apply(df)
        # Sell on the next day after a buy signal
        return entry_mask.shift(-1).fillna(False)
