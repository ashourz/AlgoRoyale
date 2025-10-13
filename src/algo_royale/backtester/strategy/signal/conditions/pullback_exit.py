import itertools

import pandas as pd
from optuna import Trial

from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.logging.loggable import Loggable


class PullbackExitCondition(StrategyCondition):
    def __init__(
        self,
        entry_condition: PullbackEntryCondition,
        logger: Loggable = None,
    ):
        super().__init__(entry_condition=entry_condition, logger=logger)
        self.entry_condition = entry_condition

    @property
    def required_columns(self):
        return self.entry_condition.required_columns

    @property
    def window_size(self) -> int:
        """Override to specify the window size for pullback exit logic."""
        return self.entry_condition.window_size

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        entry_mask = self.entry_condition.apply(df)
        # Sell on the next day after a buy signal
        return entry_mask.shift(-1).fillna(False)

    @classmethod
    def available_param_grid(cls) -> dict:
        param_grid = PullbackEntryCondition.available_param_grid()
        ma_cols = param_grid["ma_col"]
        close_cols = param_grid["close_col"]

        entry_conditions = [
            PullbackEntryCondition(ma_col=ma_col, close_col=close_col)
            for ma_col, close_col in itertools.product(ma_cols, close_cols)
        ]
        return {"entry_condition": entry_conditions}

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
            entry_condition=PullbackEntryCondition.optuna_suggest(
                logger=logger, trial=trial, prefix=f"{prefix}entry_condition_"
            ),
        )
