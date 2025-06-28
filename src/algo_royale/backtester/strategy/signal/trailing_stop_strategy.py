from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.boolean_column_entry import (
    BooleanColumnEntryCondition,
)
from algo_royale.strategy_factory.conditions.trend_above_sma import (
    TrendAboveSMACondition,
)
from algo_royale.strategy_factory.strategies.base_signal_strategy import (
    BaseSignalStrategy,
)


class TrailingStopStrategy(BaseSignalStrategy):
    """
    Combines conditions and logic for a Trailing Stop strategy.
    This strategy uses a combination of entry conditions based on boolean columns,
    trend conditions based on price above a simple moving average (SMA),
    and does not include any filter conditions or exit conditions.
    It focuses on maintaining a position as long as the price is above the SMA,
    with the potential for a trailing stop mechanism.
    """

    def __init__(
        self,
        entry_conditions: list[BooleanColumnEntryCondition] = [
            BooleanColumnEntryCondition(entry_col=StrategyColumns.ENTRY_SIGNAL)
        ],
        trend_conditions: list[TrendAboveSMACondition] = [
            TrendAboveSMACondition(
                price_col=StrategyColumns.CLOSE_PRICE, sma_col=StrategyColumns.SMA_200
            )
        ],
    ):
        super().__init__(
            entry_conditions=entry_conditions,
            trend_conditions=trend_conditions,
        )
