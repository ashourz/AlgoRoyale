from algo_royale.backtester.strategy.signal.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.backtester.strategy.signal.volume_surge_strategy import (
    VolumeSurgeStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class VolumeSurgeStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Volume Surge strategy.
    This strategy uses a combination of entry conditions based on volume surges.
    It does not include any filter conditions, trend conditions, or exit conditions,
    focusing solely on the volume surge entry logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=VolumeSurgeStrategy,
            filter_condition_types=[],
            entry_condition_types=[VolumeSurgeEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[],
            stateful_logic_types=[],
        )
