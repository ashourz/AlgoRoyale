from algo_royale.strategy_factory.combinator.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.strategy_factory.conditions.momentum_entry import (
    MomentumEntryCondition,
)
from algo_royale.strategy_factory.conditions.momentum_exit import MomentumExitCondition
from algo_royale.strategy_factory.strategies.momentum_strategy import MomentumStrategy


class MomentumStrategyCombinator(SignalStrategyCombinator):
    """
    Combines conditions and logic for a Momentum strategy.
    This strategy uses a combination of entry and exit conditions based on momentum indicators.
    It does not include any filter conditions or trend conditions, focusing solely on the momentum logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [MomentumEntryCondition]
    trend_condition_types = []  # No trend conditions for this strategy
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [MomentumExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = MomentumStrategy
