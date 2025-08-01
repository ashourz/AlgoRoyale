from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.boolean_column_entry import (
    BooleanColumnEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.trend_above_sma import (
    TrendAboveSMACondition,
)
from algo_royale.logging.loggable import Loggable


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
        logger: Loggable,
        entry_conditions: list[BooleanColumnEntryCondition] = [
            BooleanColumnEntryCondition(entry_col=SignalStrategyColumns.ENTRY_SIGNAL)
        ],
        trend_conditions: list[TrendAboveSMACondition] = [
            TrendAboveSMACondition(
                price_col=SignalStrategyColumns.CLOSE_PRICE,
                sma_col=SignalStrategyColumns.SMA_200,
            )
        ],
    ):
        super().__init__(
            entry_conditions=entry_conditions,
            trend_conditions=trend_conditions,
            logger=logger,
        )
