from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.wick_reversal_entry import (
    WickReversalEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.wick_reversal_exit import (
    WickReversalExitCondition,
)


class WickReversalStrategy(BaseSignalStrategy):
    """
    Wick Reversal Strategy:
    - Buy when the lower wick is significantly larger than the body of the candle.
    - Sell when the upper wick is significantly larger than the body of the candle.
    - Hold otherwise.
    """

    def __init__(
        self,
        entry_conditions: list[WickReversalEntryCondition] = [
            WickReversalEntryCondition(
                wick_body_ratio=2.0,
                lower_wick_col=StrategyColumns.LOWER_WICK,
                body_col=StrategyColumns.BODY,
            )
        ],
        exit_conditions: list[WickReversalExitCondition] = [
            WickReversalExitCondition(
                wick_body_ratio=2.0,
                upper_wick_col=StrategyColumns.UPPER_WICK,
                body_col=StrategyColumns.BODY,
            )
        ],
    ):
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
