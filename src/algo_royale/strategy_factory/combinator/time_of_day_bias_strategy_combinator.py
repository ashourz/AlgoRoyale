from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.time_of_day_entry import (
    TimeOfDayEntryCondition,
)
from algo_royale.strategy_factory.conditions.time_of_day_exit import (
    TimeOfDayExitCondition,
)
from algo_royale.strategy_factory.strategies.time_of_day_bias_strategy import (
    TimeOfDayBiasStrategy,
)


class TimeOfDayBiasStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Time of Day Bias strategy.
    This strategy uses a combination of entry and exit conditions based on specific hours of the day.
    It does not include any filter conditions or trend conditions, focusing solely on the time of day logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = [TimeOfDayEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    exit_condition_types = [TimeOfDayExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = TimeOfDayBiasStrategy
