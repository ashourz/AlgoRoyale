from typing import Optional

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.conditions.sma_trend import (
    SMATrendCondition,
)
from algo_royale.backtester.strategy.signal.stateful_logic.macd_trailing_stateful_logic import (
    MACDTrailingStatefulLogic,
)


class MACDTrailingStopStrategy(BaseSignalStrategy):
    """
    MACD Strategy with Trailing Stop and Modular Trend Conditions.

    Buy when MACD crosses above signal line AND all trend conditions are met.
    Sell when MACD crosses below signal line OR trailing stop triggers.

    Parameters:
        fast (int): Fast EMA period for MACD.
        slow (int): Slow EMA period for MACD.
        signal (int): Signal line period for MACD.
        stop_pct (float): Percentage for trailing stop loss.
        close_col (StrategyColumns): Column to use for closing prices.
        sma_fast_col (StrategyColumns): Column for fast SMA.
        sma_slow_col (StrategyColumns): Column for slow SMA.
    """

    def __init__(
        self,
        entry_conditions: Optional[list[StrategyCondition]] = None,
        trend_conditions=[
            SMATrendCondition(
                sma_fast_col=SignalStrategyColumns.SMA_50,
                sma_slow_col=SignalStrategyColumns.SMA_200,
            )
        ],
        stateful_logic=MACDTrailingStatefulLogic(
            fast=12,
            slow=26,
            signal=9,
            stop_pct=0.02,
            close_col=SignalStrategyColumns.CLOSE_PRICE,
        ),
        debug: bool = False,
    ):
        # Store the condition(s) as attributes
        self.entry_conditions = entry_conditions if entry_conditions else []
        self.trend_conditions = trend_conditions if trend_conditions else []
        self.stateful_logic = stateful_logic
        # Pass to base class
        super().__init__(
            entry_conditions=self.entry_conditions,
            trend_conditions=self.trend_conditions,
            stateful_logic=self.stateful_logic,
            debug=debug,
        )
