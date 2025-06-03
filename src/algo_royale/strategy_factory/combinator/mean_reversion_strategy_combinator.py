from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.price_above_sma import (
    PriceAboveSMACondition,
)
from algo_royale.strategy_factory.stateful_logic.mean_reversion_stategul_logic import (
    MeanReversionStatefulLogic,
)
from algo_royale.strategy_factory.strategies.mean_revision_strategy import (
    MeanReversionStrategy,
)


class MeanReversionStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Mean Reversion strategy.
    This strategy uses a combination of trend conditions and stateful logic for mean reversion.
    It does not include any filter conditions, entry conditions, or exit conditions.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = []  # No specific entry conditions, will use trend conditions
    trend_condition_types = [PriceAboveSMACondition]
    exit_condition_types = []  # No exit conditions for this strategy
    stateful_logic_types = [MeanReversionStatefulLogic]
    strategy_class = MeanReversionStrategy
