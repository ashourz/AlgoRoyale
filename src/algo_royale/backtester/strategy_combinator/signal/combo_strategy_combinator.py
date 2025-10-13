from algo_royale.backtester.strategy.signal.combo_strategy import ComboStrategy
from algo_royale.backtester.strategy.signal.conditions.combo_entry import (
    ComboEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_exit import (
    ComboExitCondition,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class ComboStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Combo strategy.
    This strategy uses a combination of entry and exit conditions based on multiple indicators.
    It does not include any filter conditions or trend conditions, focusing solely on the combo logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=ComboStrategy,
            filter_condition_types=[],
            entry_condition_types=[ComboEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[ComboExitCondition],
            stateful_logic_types=[],
        )
