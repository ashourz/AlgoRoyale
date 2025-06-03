from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.sma_trend import SMATrendCondition
from algo_royale.strategy_factory.stateful_logic.macd_trailing_stateful_logic import (
    MACDTrailingStatefulLogic,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class MACDTrailingStopStrategy(Strategy):
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
        fast=12,
        slow=26,
        signal=9,
        stop_pct=0.02,
        close_col=StrategyColumns.CLOSE_PRICE,
        sma_fast_col=StrategyColumns.SMA_50,
        sma_slow_col=StrategyColumns.SMA_200,
    ):
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.stop_pct = stop_pct
        # Store the condition(s) as attributes
        self.trend_conditions = [
            SMATrendCondition(sma_fast_col=sma_fast_col, sma_slow_col=sma_slow_col)
        ]

        self.stateful_logic = MACDTrailingStatefulLogic(
            close_col=close_col,
            fast=fast,
            slow=slow,
            signal=signal,
            stop_pct=stop_pct,
        )
        # Pass to base class
        super().__init__(
            trend_conditions=self.trend_conditions,
            stateful_logic=self.stateful_logic,
        )
