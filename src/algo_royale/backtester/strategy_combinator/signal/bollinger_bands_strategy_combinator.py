from algo_royale.backtester.strategy.signal.bollinger_bands_strategy import (
    BollingerBandsStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.sma_trend import (
    SMATrendCondition,
)
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class BollingerBandsStrategyCombinator(SignalStrategyCombinator):
    """Combines conditions and logic for a Bollinger Bands strategy.
    This strategy uses a combination of entry conditions based on Bollinger Bands,
    trend conditions based on SMA, and exit conditions based on Bollinger Bands.
    It does not include any filter conditions or stateful logic.
    """

    def __init__(self):
        super().__init__(
            strategy_class=BollingerBandsStrategy,
            filter_condition_types=[],
            entry_condition_types=[BollingerBandsEntryCondition],
            trend_condition_types=[SMATrendCondition],
            exit_condition_types=[BollingerBandsExitCondition],
            stateful_logic_types=[],
        )
