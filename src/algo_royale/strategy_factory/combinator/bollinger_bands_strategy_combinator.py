from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)
from algo_royale.strategy_factory.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.strategy_factory.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
)
from algo_royale.strategy_factory.conditions.sma_trend import SMATrendCondition
from algo_royale.strategy_factory.strategies.bollinger_bands_strategy import (
    BollingerBandsStrategy,
)


class BollingerBandsStrategyCombinator(StrategyCombinator):
    """Combines conditions and logic for a Bollinger Bands strategy.
    This strategy uses a combination of entry conditions based on Bollinger Bands,
    trend conditions based on SMA, and exit conditions based on Bollinger Bands.
    It does not include any filter conditions or stateful logic.
    """

    filter_condition_types = []  # No filter conditions for this strategy
    allow_empty_filter = True  # Allow empty filter conditions
    entry_condition_types = [BollingerBandsEntryCondition]
    trend_condition_types = [SMATrendCondition]
    allow_empty_trend = True  # Allow empty trend conditions
    exit_condition_types = [BollingerBandsExitCondition]
    stateful_logic_types = []  # No stateful logic for this strategy
    allow_empty_stateful_logic = True  # Allow empty stateful logic
    strategy_class = BollingerBandsStrategy
