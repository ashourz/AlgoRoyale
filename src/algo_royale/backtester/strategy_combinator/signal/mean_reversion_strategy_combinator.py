from algo_royale.backtester.strategy.signal.conditions.price_above_sma import (
    PriceAboveSMACondition,
)
from algo_royale.backtester.strategy.signal.mean_revision_strategy import (
    MeanReversionStrategy,
)
from algo_royale.backtester.strategy.signal.stateful_logic.mean_reversion_stategul_logic import (
    MeanReversionStatefulLogic,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class MeanReversionStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Mean Reversion strategy.
    This strategy uses a combination of trend conditions and stateful logic for mean reversion.
    It does not include any filter conditions, entry conditions, or exit conditions.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = []  # No specific entry conditions, will use trend conditions
    allow_empty_entry = True  # Allow empty entry conditions
    trend_condition_types = [PriceAboveSMACondition]
    exit_condition_types = []  # No exit conditions for this strategy
    allow_empty_exit = True  # Allow empty exit conditions
    stateful_logic_types = [MeanReversionStatefulLogic]
    strategy_class = MeanReversionStrategy
