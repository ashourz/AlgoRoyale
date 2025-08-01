from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.bollinger_bands_strategy_combinator import (
    BollingerBandsStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.combo_strategy_combinator import (
    ComboStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.macd_trailing_strategy_combinator import (
    MACDTrailingStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.mean_reversion_strategy_combinator import (
    MeanReversionStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.momentum_strategy_combinator import (
    MomentumStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.moving_average_crossover_strategy_combinator import (
    MovingAverageCrossoverStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.moving_average_strategy_combinator import (
    MovingAverageStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.pullback_entry_strategy_combinator import (
    PullbackEntryStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.rsi_strategy_combinator import (
    RSIStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.time_of_day_bias_strategy_combinator import (
    TimeOfDayBiasStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.trailing_stop_strategy_combinator import (
    TrailingStopStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.trend_scraper_strategy_combinator import (
    TrendScraperStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.volatility_breakout_strategy_combinator import (
    VolatilityBreakoutStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.volume_surge_strategy_combinator import (
    VolumeSurgeStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.vwap_reversion_strategy_combinator import (
    VWAPReversionStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.wick_reversal_strategy_combinator import (
    WickReversalStrategyCombinator,
)

SIGNAL_STRATEGY_COMBINATOR_MAP: dict[str, type[SignalStrategyCombinator]] = {
    "BollingerBandsStrategyCombinator": BollingerBandsStrategyCombinator,
    "ComboStrategyCombinator": ComboStrategyCombinator,
    "MACDTrailingStrategyCombinator": MACDTrailingStrategyCombinator,
    "MeanReversionStrategyCombinator": MeanReversionStrategyCombinator,
    "MomentumStrategyCombinator": MomentumStrategyCombinator,
    "MovingAverageCrossoverStrategyCombinator": MovingAverageCrossoverStrategyCombinator,
    "MovingAverageStrategyCombinator": MovingAverageStrategyCombinator,
    "PullbackEntryStrategyCombinator": PullbackEntryStrategyCombinator,
    "RSIStrategyCombinator": RSIStrategyCombinator,
    "TimeOfDayBiasStrategyCombinator": TimeOfDayBiasStrategyCombinator,
    "TrailingStopStrategyCombinator": TrailingStopStrategyCombinator,
    "TrendScraperStrategyCombinator": TrendScraperStrategyCombinator,
    "VolatilityBreakoutStrategyCombinator": VolatilityBreakoutStrategyCombinator,
    "VolumeSurgeStrategyCombinator": VolumeSurgeStrategyCombinator,
    "VWAPReversionStrategyCombinator": VWAPReversionStrategyCombinator,
    "WickReversalStrategyCombinator": WickReversalStrategyCombinator,
}
