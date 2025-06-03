from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.momentum_entry import (
    MomentumEntryCondition,
)
from algo_royale.strategy_factory.conditions.momentum_exit import MomentumExitCondition
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class MomentumStrategy(Strategy):
    """
    Enhanced Momentum Strategy using modular entry/exit conditions.
    Buy when momentum exceeds a threshold after smoothing,
    sell when momentum falls below a threshold after smoothing,
    otherwise hold.
    Parameters:
    - close_col: Column name for the closing prices.
    - lookback: Lookback period for momentum calculation (default is 10).
    - threshold: Threshold for momentum to trigger buy/sell signals (default is 0.0).
    - smooth_window: Optional smoothing window for momentum (default is None).
    - confirmation_periods: Number of periods to confirm entry/exit signals (default is 1).
    This strategy allows for modular entry and exit conditions,
    enabling easy adjustments to the momentum calculation and confirmation logic.
    It can be used as a standalone strategy or as part of a larger trading system.
    It is designed to be flexible and adaptable to different market conditions.
    """

    def __init__(
        self,
        entry_conditions: list[MomentumEntryCondition] = [
            MomentumEntryCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                lookback=10,
                threshold=0.0,
                smooth_window=None,
                confirmation_periods=1,
            )
        ],
        exit_conditions: list[MomentumExitCondition] = [
            MomentumExitCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                lookback=10,
                threshold=0.0,
                smooth_window=None,
                confirmation_periods=1,
            )
        ],
    ):
        """Initialize the Momentum Strategy with modular entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
