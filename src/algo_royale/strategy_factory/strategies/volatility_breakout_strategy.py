from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.volatility_breakout_entry import (
    VolatilityBreakoutEntryCondition,
)
from algo_royale.strategy_factory.conditions.volatility_breakout_exit import (
    VolatilityBreakoutExitCondition,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class VolatilityBreakoutStrategy(Strategy):
    """
    Volatility Breakout Strategy:
    - Buy when price breaks above a volatility threshold and is above SMA.
    - Sell when price breaks above volatility threshold but is below SMA.
    - Hold otherwise.
    """

    def __init__(
        self,
        entry_conditions: list[VolatilityBreakoutEntryCondition] = [
            VolatilityBreakoutEntryCondition(
                threshold=1.5, sma_col=StrategyColumns.SMA_20
            )
        ],
        exit_conditions: list[VolatilityBreakoutExitCondition] = [
            VolatilityBreakoutExitCondition(
                threshold=1.5, sma_col=StrategyColumns.SMA_20
            )
        ],
    ):
        """Initialize the Volatility Breakout Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
