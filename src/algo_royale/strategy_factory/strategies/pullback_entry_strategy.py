from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.strategy_factory.conditions.pullback_exit import PullbackExitCondition
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class PullbackEntryStrategy(Strategy):
    def __init__(
        self,
        entry_conditions: list[PullbackEntryCondition] = [
            PullbackEntryCondition(
                ma_col=StrategyColumns.SMA_20, close_col=StrategyColumns.CLOSE_PRICE
            )
        ],
    ) -> None:
        """Initialize the Pullback Entry Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        """
        self.entry_conditions = entry_conditions
        self.entry_condition = entry_conditions[0] if entry_conditions else None
        if not self.entry_condition:
            raise ValueError("Entry conditions must not be empty.")
        self.exit_conditions = [
            PullbackExitCondition(entry_condition=self.entry_condition)
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
