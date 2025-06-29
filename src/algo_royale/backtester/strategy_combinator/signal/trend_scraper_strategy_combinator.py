from algo_royale.backtester.strategy.signal.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingCondition,
)
from algo_royale.backtester.strategy.signal.conditions.return_volatility_exit import (
    ReturnVolatilityExitCondition,
)
from algo_royale.backtester.strategy.signal.trend_scraper_strategy import (
    TrendScraperStrategy,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class TrendScraperStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Trend Scraper strategy.
    This strategy uses a combination of trend conditions and exit conditions.
    It does not include any filter conditions or entry conditions, focusing solely on the trend and exit logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = []  # No entry conditions for this strategy
    allow_empty_entry = True  # Allow empty entry conditions
    trend_condition_types = [EMAAboveSMARollingCondition]
    exit_condition_types = [ReturnVolatilityExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = TrendScraperStrategy
