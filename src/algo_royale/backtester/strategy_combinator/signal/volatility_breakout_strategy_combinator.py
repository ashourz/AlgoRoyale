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

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [VolatilityBreakoutEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [VolatilityBreakoutExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = VolatilityBreakoutStrategy
