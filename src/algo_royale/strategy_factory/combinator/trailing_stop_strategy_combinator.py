from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.boolean_column_entry import (
    BooleanColumnEntryCondition,
)
from algo_royale.strategy_factory.conditions.momentum_entry import (
    MomentumEntryCondition,
)
from algo_royale.strategy_factory.conditions.momentum_exit import MomentumExitCondition
from algo_royale.strategy_factory.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.strategy_factory.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.strategy_factory.conditions.rsi_exit import RSIExitCondition
from algo_royale.strategy_factory.conditions.sma_trend import SMATrendCondition
from algo_royale.strategy_factory.conditions.trailing_stop_exit_condition import (
    TrailingStopExitCondition,
)
from algo_royale.strategy_factory.conditions.trend_above_sma import (
    TrendAboveSMACondition,
)
from algo_royale.strategy_factory.stateful_logic.trailing_stop_stateful_logic import (
    TrailingStopStatefulLogic,
)
from algo_royale.strategy_factory.strategies.trailing_stop_strategy import (
    TrailingStopStrategy,
)


class TrailingStopStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Trailing Stop strategy.
    This strategy uses a combination of entry conditions based on boolean columns,
    trend conditions based on price above a simple moving average (SMA),
    and does not include any filter conditions or exit conditions."""

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [
        BooleanColumnEntryCondition,
        MomentumEntryCondition,
        PullbackEntryCondition,
        MovingAverageEntryCondition,
    ]
    trend_condition_types = [TrendAboveSMACondition, SMATrendCondition]
    exit_condition_types = [
        TrailingStopExitCondition,
        MovingAverageExitCondition,
        RSIExitCondition,
        MomentumExitCondition,
    ]
    allow_empty_exit = True  # Allow empty exit conditions
    stateful_logic_types = [TrailingStopStatefulLogic]
    strategy_class = TrailingStopStrategy
