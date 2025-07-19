from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_entry import (
    RSIEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_exit import RSIExitCondition


class RSIStrategy(BaseSignalStrategy):
    """
    Relative Strength Index (RSI) Strategy

    Generates buy/sell signals based on RSI indicator thresholds.
    Buy when RSI is below oversold threshold, sell when above overbought.
    """

    def __init__(
        self,
        entry_conditions: list[RSIEntryCondition] = [
            RSIEntryCondition(
                close_col=SignalStrategyColumns.CLOSE_PRICE, period=14, oversold=30
            )
        ],
        exit_conditions: list[RSIExitCondition] = [
            RSIExitCondition(
                close_col=SignalStrategyColumns.CLOSE_PRICE, period=14, overbought=70
            )
        ],
        debug: bool = False,
    ) -> None:
        """Initialize the RSI Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            debug=debug,
        )
