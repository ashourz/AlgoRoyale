from algo_royale.backtester.strategy.signal.conditions.time_of_day_entry import (
    TimeOfDayEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.time_of_day_exit import (
    TimeOfDayExitCondition,
)
from algo_royale.backtester.strategy.signal.time_of_day_bias_strategy import (
    TimeOfDayBiasStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class TimeOfDayBiasStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Time of Day Bias strategy.
    This strategy uses a combination of entry and exit conditions based on specific hours of the day.
    It does not include any filter conditions or trend conditions, focusing solely on the time of day logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=TimeOfDayBiasStrategy,
            filter_condition_types=[],
            entry_condition_types=[TimeOfDayEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[TimeOfDayExitCondition],
            stateful_logic_types=[],
        )
