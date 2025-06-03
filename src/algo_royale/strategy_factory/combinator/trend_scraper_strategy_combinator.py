from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingCondition,
)
from algo_royale.strategy_factory.conditions.return_volatility_exit import (
    ReturnVolatilityExitCondition,
)
from algo_royale.strategy_factory.strategies.trend_scraper_strategy import (
    TrendScraperStrategy,
)


class TrendScraperStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Trend Scraper strategy.
    This strategy uses a combination of trend conditions and exit conditions.
    It does not include any filter conditions or entry conditions, focusing solely on the trend and exit logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    entry_condition_types = []  # No entry conditions for this strategy
    trend_condition_types = [EMAAboveSMARollingCondition]
    exit_condition_types = [ReturnVolatilityExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    strategy_class = TrendScraperStrategy
