from enum import Enum


class FeatureInfo:
    def __init__(self, value: str, full_name: str, description: str):
        self.value = value  # The column/key used in your DataFrame
        self.full_name = full_name  # Human-readable name
        self.description = description  # What the feature is and its significance

    def __str__(self):
        return f"{self.value}: {self.full_name} - {self.description}"


class FeatureName(Enum):
    PCT_RETURN = FeatureInfo(
        "pct_return",
        "Percentage Return",
        "The percent change in close price from the previous period, measuring short-term momentum.",
    )
    LOG_RETURN = FeatureInfo(
        "log_return",
        "Logarithmic Return",
        "The natural log of close price change, useful for additive returns in time-series analysis.",
    )
    SMA_20 = FeatureInfo(
        "sma_20",
        "Simple Moving Average (20)",
        "The average of the last 20 close prices, indicating medium-term trend direction.",
    )
    EMA_20 = FeatureInfo(
        "ema_20",
        "Exponential Moving Average (20)",
        "A moving average giving more weight to recent prices, indicating recent trend strength.",
    )
    VOLATILITY_20 = FeatureInfo(
        "volatility_20",
        "Volatility (20)",
        "Standard deviation of percentage returns over 20 periods, measuring price variability.",
    )
    RANGE = FeatureInfo(
        "range",
        "Price Range",
        "The difference between the high and low price in a period, indicating intrabar volatility.",
    )
    BODY = FeatureInfo(
        "body",
        "Candle Body",
        "The absolute difference between open and close prices, showing trend strength within the bar.",
    )
    UPPER_WICK = FeatureInfo(
        "upper_wick",
        "Upper Wick",
        "The distance from the candle's top (high) to the higher of open/close, capturing upside volatility.",
    )
    LOWER_WICK = FeatureInfo(
        "lower_wick",
        "Lower Wick",
        "The distance from the candle's bottom (low) to the lower of open/close, capturing downside volatility.",
    )
    VOL_MA_20 = FeatureInfo(
        "vol_ma_20",
        "Volume Moving Average (20)",
        "The average of the last 20 volumes, highlighting typical trading activity.",
    )
    VOL_CHANGE = FeatureInfo(
        "vol_change",
        "Volume Change",
        "The percent change in volume from the previous period, signaling unusual trading activity.",
    )
    VWAP_20 = FeatureInfo(
        "vwap_20",
        "Volume Weighted Average Price (20)",
        "The rolling 20-period VWAP, reflecting average transaction price weighted by volume.",
    )
    HOUR = FeatureInfo(
        "hour",
        "Hour of Day",
        "The hour extracted from the timestamp, to capture intraday patterns or regime changes.",
    )
    DAY_OF_WEEK = FeatureInfo(
        "day_of_week",
        "Day of Week",
        "The day of the week extracted from the timestamp, useful for weekly seasonality.",
    )


# # Example usage:
# for feature in FeatureName:
#     print(f"{feature.value.value}: {feature.value.full_name} - {feature.value.description}")
