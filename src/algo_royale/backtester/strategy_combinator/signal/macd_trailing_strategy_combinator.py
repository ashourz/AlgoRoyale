from algo_royale.backtester.strategy.signal.conditions.sma_trend import (
    SMATrendCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.backtester.strategy.signal.macd_trailing_strategy import (
    MACDTrailingStopStrategy,
)
from algo_royale.backtester.strategy.signal.stateful_logic.macd_trailing_stateful_logic import (
    MACDTrailingStatefulLogic,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class MACDTrailingStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a MACD Trailing Stop strategy.
    This strategy uses a combination of entry conditions based on volume surges,
    trend conditions based on SMA, and stateful logic for MACD trailing stops.
    It does not include any filter conditions or exit conditions.
    """

    def __init__(self):
        super().__init__(
            filter_condition_types=[],
            entry_condition_types=[VolumeSurgeEntryCondition],
            trend_condition_types=[SMATrendCondition],
            exit_condition_types=[],
            stateful_logic_types=[MACDTrailingStatefulLogic],
        )
        self.strategy_class = MACDTrailingStopStrategy
