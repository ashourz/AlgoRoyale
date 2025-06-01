from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.pullback_entry import PullbackEntryCondition
from algo_royale.strategies.conditions.pullback_exit import PullbackExitCondition


class PullbackEntryStrategy(Strategy):
    def __init__(
        self,
        ma_col: str = StrategyColumns.SMA_20,
        close_col: str = StrategyColumns.CLOSE_PRICE,
    ) -> None:
        self.ma_col = ma_col
        self.close_col = close_col

        entry_condition = PullbackEntryCondition(ma_col=ma_col, close_col=close_col)
        exit_condition = PullbackExitCondition(entry_condition=entry_condition)

        self.entry_conditions = [entry_condition]
        self.exit_conditions = [exit_condition]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
