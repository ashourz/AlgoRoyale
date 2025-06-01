from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.volatility_breakout_entry import (
    VolatilityBreakoutEntryCondition,
)
from algo_royale.strategies.conditions.volatility_breakout_exit import (
    VolatilityBreakoutExitCondition,
)


class VolatilityBreakoutStrategy(Strategy):
    """
    Volatility Breakout Strategy:
    - Buy when price breaks above a volatility threshold and is above SMA.
    - Sell when price breaks above volatility threshold but is below SMA.
    - Hold otherwise.
    """

    def __init__(
        self, threshold: float = 1.5, sma_col: StrategyColumns = StrategyColumns.SMA_20
    ):
        self.threshold = threshold
        self.sma_col = sma_col

        self.entry_conditions = [
            VolatilityBreakoutEntryCondition(threshold=threshold, sma_col=sma_col)
        ]
        self.exit_conditions = [
            VolatilityBreakoutExitCondition(threshold=threshold, sma_col=sma_col)
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
