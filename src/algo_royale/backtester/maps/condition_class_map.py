from algo_royale.backtester.strategy.signal.conditions.adx_above_threshold import (
    ADXAboveThresholdCondition,
)
from algo_royale.backtester.strategy.signal.conditions.adx_below_threshold import (
    ADXBelowThresholdCondition,
)
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.boolean_column_entry import (
    BooleanColumnEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_entry import (
    ComboEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_exit import (
    ComboExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingCondition,
)
from algo_royale.backtester.strategy.signal.conditions.macd_bearish_cross import (
    MACDBearishCrossCondition,
)
from algo_royale.backtester.strategy.signal.conditions.macd_bullish_cross import (
    MACDBullishCrossCondition,
)
from algo_royale.backtester.strategy.signal.conditions.momentum_entry import (
    MomentumEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.momentum_exit import (
    MomentumExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_crossover_entry import (
    MovingAverageCrossoverEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_crossover_exit import (
    MovingAverageCrossoverExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.price_above_sma import (
    PriceAboveSMACondition,
)
from algo_royale.backtester.strategy.signal.conditions.price_below_sma import (
    PriceBelowSMACondition,
)
from algo_royale.backtester.strategy.signal.conditions.price_crosses_above_sma import (
    PriceCrossesAboveSMACondition,
)
from algo_royale.backtester.strategy.signal.conditions.price_crosses_below_sma import (
    PriceCrossesBelowSMACondition,
)
from algo_royale.backtester.strategy.signal.conditions.pullback_entry import (
    PullbackEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.pullback_exit import (
    PullbackExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.return_volatility_exit import (
    ReturnVolatilityExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_above_threshold import (
    RSIAboveThresholdCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_below_threshold import (
    RSIBelowThresholdCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_entry import (
    RSIEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.rsi_exit import RSIExitCondition
from algo_royale.backtester.strategy.signal.conditions.sma_trend import (
    SMATrendCondition,
)
from algo_royale.backtester.strategy.signal.conditions.time_of_day_entry import (
    TimeOfDayEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.time_of_day_exit import (
    TimeOfDayExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.trailing_stop_exit_condition import (
    TrailingStopExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.trend_above_sma import (
    TrendAboveSMACondition,
)
from algo_royale.backtester.strategy.signal.conditions.volatility_breakout_entry import (
    VolatilityBreakoutEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volatility_breakout_exit import (
    VolatilityBreakoutExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volatility_spike import (
    VolatilitySpikeCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge import (
    VolumeSurgeCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge_exit import (
    VolumeSurgeExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)
from algo_royale.backtester.strategy.signal.conditions.wick_reversal_entry import (
    WickReversalEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.wick_reversal_exit import (
    WickReversalExitCondition,
)

CONDITION_CLASS_MAP: dict[str, type[StrategyCondition]] = {
    "ADXAboveThresholdCondition": ADXAboveThresholdCondition,
    "ADXBelowThresholdCondition": ADXBelowThresholdCondition,
    "BollingerBandsEntryCondition": BollingerBandsEntryCondition,
    "BollingerBandsExitCondition": BollingerBandsExitCondition,
    "BooleanColumnEntryCondition": BooleanColumnEntryCondition,
    "ComboEntryCondition": ComboEntryCondition,
    "ComboExitCondition": ComboExitCondition,
    "EMAAboveSMARollingCondition": EMAAboveSMARollingCondition,
    "MACDBearishCrossCondition": MACDBearishCrossCondition,
    "MACDBullishCrossCondition": MACDBullishCrossCondition,
    "MomentumEntryCondition": MomentumEntryCondition,
    "MomentumExitCondition": MomentumExitCondition,
    "MovingAverageCrossoverEntryCondition": MovingAverageCrossoverEntryCondition,
    "MovingAverageCrossoverExitCondition": MovingAverageCrossoverExitCondition,
    "MovingAverageEntryCondition": MovingAverageEntryCondition,
    "MovingAverageExitCondition": MovingAverageExitCondition,
    "PriceAboveSMACondition": PriceAboveSMACondition,
    "PriceBelowSMACondition": PriceBelowSMACondition,
    "PriceCrossesAboveSMACondition": PriceCrossesAboveSMACondition,
    "PriceCrossesBelowSMACondition": PriceCrossesBelowSMACondition,
    "PullbackEntryCondition": PullbackEntryCondition,
    "PullbackExitCondition": PullbackExitCondition,
    "ReturnVolatilityExitCondition": ReturnVolatilityExitCondition,
    "RSIAboveThresholdCondition": RSIAboveThresholdCondition,
    "RSIBelowThresholdCondition": RSIBelowThresholdCondition,
    "RSIEntryCondition": RSIEntryCondition,
    "RSIExitCondition": RSIExitCondition,
    "SMATrendCondition": SMATrendCondition,
    "TimeOfDayEntryCondition": TimeOfDayEntryCondition,
    "TimeOfDayExitCondition": TimeOfDayExitCondition,
    "TrailingStopExitCondition": TrailingStopExitCondition,
    "TrendAboveSMACondition": TrendAboveSMACondition,
    "VolatilityBreakoutEntryCondition": VolatilityBreakoutEntryCondition,
    "VolatilityBreakoutExitCondition": VolatilityBreakoutExitCondition,
    "VolatilitySpikeCondition": VolatilitySpikeCondition,
    "VolumeSurgeEntryCondition": VolumeSurgeEntryCondition,
    "VolumeSurgeExitCondition": VolumeSurgeExitCondition,
    "VolumeSurgeCondition": VolumeSurgeCondition,
    "VWAPReversionEntryCondition": VWAPReversionEntryCondition,
    "VWAPReversionExitCondition": VWAPReversionExitCondition,
    "WickReversalEntryCondition": WickReversalEntryCondition,
    "WickReversalExitCondition": WickReversalExitCondition,
}
