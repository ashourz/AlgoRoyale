from algo_royale.backtester.strategy.signal.conditions.price_above_sma import (
    PriceAboveSMACondition,
)
from algo_royale.backtester.strategy.signal.mean_revision_strategy import (
    MeanReversionStrategy,
)
from algo_royale.backtester.strategy.signal.stateful_logic.mean_reversion_stateful_logic import (
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

    def __init__(self):
        super().__init__(
            filter_condition_types=[],
            entry_condition_types=[],
            trend_condition_types=[PriceAboveSMACondition],
            exit_condition_types=[],
            stateful_logic_types=[MeanReversionStatefulLogic],
        )
        self.strategy_class = MeanReversionStrategy
