from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.volatility_breakout_entry import (
    VolatilityBreakoutEntryCondition,
)
from algo_royale.strategy_factory.conditions.volatility_breakout_exit import (
    VolatilityBreakoutExitCondition,
)
from algo_royale.strategy_factory.strategies.volatility_breakout_strategy import (
    VolatilityBreakoutStrategy,
)


class VolatilityBreakoutStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Volatility Breakout strategy.
    This strategy uses a combination of entry and exit conditions based on volatility indicators.
    It does not include any filter conditions or trend conditions, focusing solely on the volatility breakout logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [VolatilityBreakoutEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = [VolatilityBreakoutExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = VolatilityBreakoutStrategy
