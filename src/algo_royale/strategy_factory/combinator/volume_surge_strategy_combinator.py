from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.strategy_factory.strategies.volume_surge_strategy import (
    VolumeSurgeStrategy,
)


class VolumeSurgeStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Volume Surge strategy.
    This strategy uses a combination of entry conditions based on volume surges.
    It does not include any filter conditions, trend conditions, or exit conditions,
    focusing solely on the volume surge entry logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [VolumeSurgeEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = []  # No exit conditions for this strategy
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = VolumeSurgeStrategy
