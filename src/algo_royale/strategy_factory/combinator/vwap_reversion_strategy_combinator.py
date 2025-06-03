from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.strategy_factory.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)
from algo_royale.strategy_factory.strategies.vwap_reversion_strategy import (
    VWAPReversionStrategy,
)


class VWAPReversionStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a VWAP Reversion strategy.
    This strategy uses a combination of entry conditions based on VWAP reversion,
    trend conditions based on volume surges, and exit conditions based on VWAP reversion.
    It does not include any filter conditions or stateful logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [VWAPReversionEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = [VWAPReversionExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = VWAPReversionStrategy
