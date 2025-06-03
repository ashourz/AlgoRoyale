from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.sma_trend import SMATrendCondition
from algo_royale.strategy_factory.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.strategy_factory.stateful_logic.macd_trailing_stateful_logic import (
    MACDTrailingStatefulLogic,
)
from algo_royale.strategy_factory.strategies.macd_trailing_strategy import (
    MACDTrailingStopStrategy,
)


class MACDTrailingStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a MACD Trailing Stop strategy.
    This strategy uses a combination of entry conditions based on volume surges,
    trend conditions based on SMA, and stateful logic for MACD trailing stops.
    It does not include any filter conditions or exit conditions.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [VolumeSurgeEntryCondition]
    allow_empty_entry = True  # Allow empty entry conditions
    trend_condition_types = [SMATrendCondition]
    exit_condition_types = []  # No exit conditions for this strategy
    stateful_logic_types = [MACDTrailingStatefulLogic]
    strategy_class = MACDTrailingStopStrategy
