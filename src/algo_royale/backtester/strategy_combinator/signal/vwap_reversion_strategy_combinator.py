from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)
from algo_royale.backtester.strategy.signal.vwap_reversion_strategy import (
    VWAPReversionStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class VWAPReversionStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a VWAP Reversion strategy.
    This strategy uses a combination of entry conditions based on VWAP reversion,
    trend conditions based on volume surges, and exit conditions based on VWAP reversion.
    It does not include any filter conditions or stateful logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=VWAPReversionStrategy,
            filter_condition_types=[],
            entry_condition_types=[VWAPReversionEntryCondition],
            trend_condition_types=[],
            exit_condition_types=[VWAPReversionExitCondition],
            stateful_logic_types=[],
        )
