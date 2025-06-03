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
    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [VolumeSurgeEntryCondition]
    trend_condition_types = [SMATrendCondition]
    exit_condition_types = []  # No exit conditions for this strategy
    stateful_logic_types = [MACDTrailingStatefulLogic]
    strategy_class = MACDTrailingStopStrategy
