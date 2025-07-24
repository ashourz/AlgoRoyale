"""
SYMBOL_STRATEGY_CLASS_MAP: Maps strategy class names (str) to their class objects.
Add new strategy classes here as needed.
"""

# --- Signal strategy imports ---
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.bollinger_bands_strategy import (
    BollingerBandsStrategy,
)
from algo_royale.backtester.strategy.signal.combo_strategy import ComboStrategy
from algo_royale.backtester.strategy.signal.macd_trailing_strategy import (
    MACDTrailingStopStrategy,
)
from algo_royale.backtester.strategy.signal.mean_revision_strategy import (
    MeanReversionStrategy,
)
from algo_royale.backtester.strategy.signal.momentum_strategy import MomentumStrategy
from algo_royale.backtester.strategy.signal.moving_average_crossover_strategy import (
    MovingAverageCrossoverStrategy,
)
from algo_royale.backtester.strategy.signal.moving_average_strategy import (
    MovingAverageStrategy,
)
from algo_royale.backtester.strategy.signal.pullback_entry_strategy import (
    PullbackEntryStrategy,
)
from algo_royale.backtester.strategy.signal.rsi_strategy import RSIStrategy
from algo_royale.backtester.strategy.signal.time_of_day_bias_strategy import (
    TimeOfDayBiasStrategy,
)
from algo_royale.backtester.strategy.signal.trailing_stop_strategy import (
    TrailingStopStrategy,
)
from algo_royale.backtester.strategy.signal.trend_scraper_strategy import (
    TrendScraperStrategy,
)
from algo_royale.backtester.strategy.signal.volatility_breakout_strategy import (
    VolatilityBreakoutStrategy,
)
from algo_royale.backtester.strategy.signal.volume_surge_strategy import (
    VolumeSurgeStrategy,
)
from algo_royale.backtester.strategy.signal.vwap_reversion_strategy import (
    VWAPReversionStrategy,
)
from algo_royale.backtester.strategy.signal.wick_reversal_strategy import (
    WickReversalStrategy,
)

# --- Add more as needed ---

SYMBOL_STRATEGY_CLASS_MAP: dict[str, type] = {
    "BaseSignalStrategy": BaseSignalStrategy,
    "BollingerBandsStrategy": BollingerBandsStrategy,
    "ComboStrategy": ComboStrategy,
    "MACDTrailingStopStrategy": MACDTrailingStopStrategy,
    "MeanReversionStrategy": MeanReversionStrategy,
    "MomentumStrategy": MomentumStrategy,
    "MovingAverageCrossoverStrategy": MovingAverageCrossoverStrategy,
    "MovingAverageStrategy": MovingAverageStrategy,
    "PullbackEntryStrategy": PullbackEntryStrategy,
    "RSIStrategy": RSIStrategy,
    "TimeOfDayBiasStrategy": TimeOfDayBiasStrategy,
    "TrailingStopStrategy": TrailingStopStrategy,
    "TrendScraperStrategy": TrendScraperStrategy,
    "VolumeSurgeStrategy": VolumeSurgeStrategy,
    "VolatilityBreakoutStrategy": VolatilityBreakoutStrategy,
    "VWAPReversionStrategy": VWAPReversionStrategy,
    "WickReversalStrategy": WickReversalStrategy,
}
