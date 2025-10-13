from algo_royale.backtester.strategy.signal.conditions.volatility_breakout_entry import (
    VolatilityBreakoutEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volatility_breakout_exit import (
    VolatilityBreakoutExitCondition,
)
from algo_royale.backtester.strategy.signal.volatility_breakout_strategy import (
    VolatilityBreakoutStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class VolatilityBreakoutStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Volatility Breakout strategy.
    This strategy uses a combination of entry and exit conditions based on volatility indicators.
    It does not include any filter conditions or trend conditions, focusing solely on the volatility breakout logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=VolatilityBreakoutStrategy,
            filter_condition_types=[],
            entry_condition_types=[VolatilityBreakoutEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[VolatilityBreakoutExitCondition],
            stateful_logic_types=[],
        )
