from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.wick_reversal_entry import (
    WickReversalEntryCondition,
)
from algo_royale.strategies.conditions.wick_reversal_exit import (
    WickReversalExitCondition,
)


class WickReversalStrategy(Strategy):
    """
    Wick Reversal Strategy:
    - Buy when the lower wick is significantly larger than the body of the candle.
    - Sell when the upper wick is significantly larger than the body of the candle.
    - Hold otherwise.
    """

    def __init__(
        self,
        wick_body_ratio: float = 2.0,
        upper_wick_col: str = StrategyColumns.UPPER_WICK,
        lower_wick_col: str = StrategyColumns.LOWER_WICK,
        body_col: str = StrategyColumns.BODY,
    ):
        self.wick_body_ratio = wick_body_ratio
        self.upper_wick_col = upper_wick_col
        self.lower_wick_col = lower_wick_col
        self.body_col = body_col

        self.entry_conditions = [
            WickReversalEntryCondition(
                wick_body_ratio=wick_body_ratio,
                lower_wick_col=lower_wick_col,
                body_col=body_col,
            )
        ]
        self.exit_conditions = [
            WickReversalExitCondition(
                wick_body_ratio=wick_body_ratio,
                upper_wick_col=upper_wick_col,
                body_col=body_col,
            )
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
