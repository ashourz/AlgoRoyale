from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.sma_trend import SMATrendCondition
from algo_royale.strategy_factory.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
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
        entry_conditions=None,
        trend_conditions=[
            SMATrendCondition(
                sma_fast_col=StrategyColumns.SMA_50,
                sma_slow_col=StrategyColumns.SMA_200,
            )
        ],
        stateful_logic=MACDTrailingStatefulLogic(
            fast=12,
            slow=26,
            signal=9,
            stop_pct=0.02,
            close_col=StrategyColumns.CLOSE_PRICE,
        ),
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
        )

    @classmethod
    def all_strategy_combinations(cls):
        """
        Generate all combinations of MACD Trailing Stop strategies with different trend conditions.
        """
        entry_variants = list(VolumeSurgeEntryCondition.all_possible_conditions()) + [
            None
        ]
        trend_variants = SMATrendCondition.all_possible_conditions()
        stateful_logics = MACDTrailingStatefulLogic.all_possible_conditions()
        strategies = []
        # Generate combinations of entry conditions, trend conditions, and stateful logic
        for entry in entry_variants:
            for trend in trend_variants:
                for stateful_logic in stateful_logics:
                    strategies.append(
                        cls(
                            entry_conditions=[entry] if entry else [],
                            trend_conditions=[trend],
                            stateful_logic=stateful_logic,
                        )
                    )
        # Return the list of strategies
        return strategies
