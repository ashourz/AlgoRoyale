from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.pullback_exit import (
    PullbackExitCondition,
)


class PullbackEntryStrategy(BaseSignalStrategy):
    def __init__(
        self,
        entry_conditions: list[PullbackEntryCondition] = [
            PullbackEntryCondition(
                ma_col=SignalStrategyColumns.SMA_20,
                close_col=SignalStrategyColumns.CLOSE_PRICE,
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
