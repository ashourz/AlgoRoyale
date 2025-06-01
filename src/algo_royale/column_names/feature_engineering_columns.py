from algo_royale.column_names.base_column_names import BaseColumnNames
from algo_royale.column_names.column_name import ColumnName


class FeatureEngineeringColumns(BaseColumnNames):
    """Column names used for feature engineering in the algorithmic trading framework."""

    # This class defines the column names used during the feature engineering stage,
    # where technical indicators and other features are derived from raw data.
    # It inherits from BaseColumnNames to maintain consistency across the framework.

    SYMBOL = ColumnName("symbol")
    RAW_EXCHANGE = ColumnName("exchange")
    TIMESTAMP = ColumnName("timestamp")
    OPEN_PRICE = ColumnName("open_price")
    HIGH_PRICE = ColumnName("high_price")
    LOW_PRICE = ColumnName("low_price")
    CLOSE_PRICE = ColumnName("close_price")
    VOLUME = ColumnName("volume")
    NUM_TRADES = ColumnName("num_trades")
    VOLUME_WEIGHTED_PRICE = ColumnName("volume_weighted_price")

    # Technical indicators
    PCT_RETURN = ColumnName(
        value="pct_return",
        full_name="Percentage Return",
        description="The percent change in close price from the previous period, measuring short-term momentum.",
    )
    LOG_RETURN = ColumnName(
        value="log_return",
        full_name="Logarithmic Return",
        description="The natural log of close price change, useful for additive returns in time-series analysis.",
    )
    SMA_20 = ColumnName(
        value="sma_20",
        full_name="Simple Moving Average (20)",
        description="The average of the last 20 close prices, indicating medium-term trend direction.",
    )
    SMA_50 = ColumnName(
        value="sma_50",
        full_name="Simple Moving Average (50)",
        description="The average of the last 50 close prices, indicating longer-term trend direction.",
    )
    SMA_200 = ColumnName(
        value="sma_200",
        full_name="Simple Moving Average (200)",
        description="The average of the last 200 close prices, indicating long-term trend direction.",
    )
    MACD = ColumnName(
        value="macd",
        full_name="Moving Average Convergence Divergence",
        description="The difference between the 12-period and 26-period exponential moving averages, indicating trend strength.",
    )
    RSI = ColumnName(
        value="rsi",
        full_name="Relative Strength Index",
        description="A momentum oscillator measuring the speed and change of price movements, indicating overbought or oversold conditions.",
    )
    EMA_20 = ColumnName(
        value="ema_20",
        full_name="Exponential Moving Average (20)",
        description="A moving average giving more weight to recent prices, indicating recent trend strength.",
    )
    VOLATILITY_20 = ColumnName(
        value="volatility_20",
        full_name="Volatility (20)",
        description="Standard deviation of percentage returns over 20 periods, measuring price variability.",
    )
    RANGE = ColumnName(
        value="range",
        full_name="Price Range",
        description="The difference between the high and low price in a period, indicating intrabar volatility.",
    )
    BODY = ColumnName(
        value="body",
        full_name="Candle Body",
        description="The absolute difference between open and close prices, showing trend strength within the bar.",
    )
    UPPER_WICK = ColumnName(
        value="upper_wick",
        full_name="Upper Wick",
        description="The distance from the candle's top (high) to the higher of open/close, capturing upside volatility.",
    )
    LOWER_WICK = ColumnName(
        value="lower_wick",
        full_name="Lower Wick",
        description="The distance from the candle's bottom (low) to the lower of open/close, capturing downside volatility.",
    )
    VOL_MA_20 = ColumnName(
        value="vol_ma_20",
        full_name="Volume Moving Average (20)",
        description="The average of the last 20 volumes, highlighting typical trading activity.",
    )
    VOL_CHANGE = ColumnName(
        value="vol_change",
        full_name="Volume Change",
        description="The percent change in volume from the previous period, signaling unusual trading activity.",
    )
    VWAP_20 = ColumnName(
        value="vwap_20",
        full_name="Volume Weighted Average Price (20)",
        description="The rolling 20-period VWAP, reflecting average transaction price weighted by volume.",
    )
    HOUR = ColumnName(
        value="hour",
        full_name="Hour of Day",
        description="The hour extracted from the timestamp, to capture intraday patterns or regime changes.",
    )
    DAY_OF_WEEK = ColumnName(
        value="day_of_week",
        full_name="Day of Week",
        description="The day of the week extracted from the timestamp, useful for weekly seasonality.",
    )
    ADX = ColumnName(
        value="adx",
        full_name="Average Directional Index",
        description="A measure of trend strength, calculated from the high, low, and close prices.",
    )
