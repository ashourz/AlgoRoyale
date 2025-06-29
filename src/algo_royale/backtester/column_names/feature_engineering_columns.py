from algo_royale.backtester.column_names.column_name import ColumnName
from algo_royale.backtester.column_names.data_ingest_columns import DataIngestColumns


class FeatureEngineeringColumns(DataIngestColumns):
    """Column names used for feature engineering in the algorithmic trading framework.
    These columns are derived from the raw data and used for technical analysis and modeling."""

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
    SMA_10 = ColumnName(
        value="sma_10",
        full_name="Simple Moving Average (10)",
        description="The average of the last 10 close prices, indicating short-term trend direction.",
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
    SMA_100 = ColumnName(
        value="sma_100",
        full_name="Simple Moving Average (100)",
        description="The average of the last 100 close prices, indicating longer-term trend direction.",
    )
    SMA_150 = ColumnName(
        value="sma_150",
        full_name="Simple Moving Average (150)",
        description="The average of the last 150 close prices, indicating longer-term trend direction.",
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
    MACD_SIGNAL = ColumnName(
        value="macd_signal",
        full_name="MACD Signal Line",
        description="The 9-period exponential moving average of the MACD line, used to identify buy/sell signals.",
    )
    RSI = ColumnName(
        value="rsi",
        full_name="Relative Strength Index",
        description="A momentum oscillator measuring the speed and change of price movements, indicating overbought or oversold conditions.",
    )
    EMA_9 = ColumnName(
        value="ema_9",
        full_name="Exponential Moving Average (9)",
        description="A short-term moving average giving more weight to recent prices, indicating immediate trend direction.",
    )
    EMA_10 = ColumnName(
        value="ema_10",
        full_name="Exponential Moving Average (10)",
        description="A short-term moving average giving more weight to recent prices, indicating immediate trend direction.",
    )
    EMA_12 = ColumnName(
        value="ema_12",
        full_name="Exponential Moving Average (12)",
        description="A short-term moving average giving more weight to recent prices, indicating immediate trend direction.",
    )
    EMA_20 = ColumnName(
        value="ema_20",
        full_name="Exponential Moving Average (20)",
        description="A moving average giving more weight to recent prices, indicating recent trend strength.",
    )
    EMA_26 = ColumnName(
        value="ema_26",
        full_name="Exponential Moving Average (26)",
        description="A longer-term moving average giving more weight to recent prices, indicating medium-term trend strength.",
    )
    EMA_50 = ColumnName(
        value="ema_50",
        full_name="Exponential Moving Average (50)",
        description="A longer-term moving average giving more weight to recent prices, indicating longer-term trend strength.",
    )
    EMA_100 = ColumnName(
        value="ema_100",
        full_name="Exponential Moving Average (100)",
        description="A longer-term moving average giving more weight to recent prices, indicating long-term trend strength.",
    )
    EMA_150 = ColumnName(
        value="ema_150",
        full_name="Exponential Moving Average (150)",
        description="A longer-term moving average giving more weight to recent prices, indicating long-term trend strength.",
    )
    EMA_200 = ColumnName(
        value="ema_200",
        full_name="Exponential Moving Average (200)",
        description="A long-term moving average giving more weight to recent prices, indicating long-term trend strength.",
    )
    VOLATILITY_10 = ColumnName(
        value="volatility_10",
        full_name="Volatility (10)",
        description="Standard deviation of percentage returns over 10 periods, measuring price variability.",
    )
    VOLATILITY_20 = ColumnName(
        value="volatility_20",
        full_name="Volatility (20)",
        description="Standard deviation of percentage returns over 20 periods, measuring price variability.",
    )
    VOLATILITY_50 = ColumnName(
        value="volatility_50",
        full_name="Volatility (50)",
        description="Standard deviation of percentage returns over 50 periods, measuring price variability.",
    )
    ATR_14 = ColumnName(
        value="atr_14",
        full_name="Average True Range (14)",
        description="A measure of volatility calculated as the average of true ranges over 14 periods, capturing price movement.",
    )
    HIST_VOLATILITY_20 = ColumnName(
        value="hist_volatility_20",
        full_name="Historical Volatility (20)",
        description="The standard deviation of log returns over the last 20 periods, indicating historical price volatility.",
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
    VOL_MA_10 = ColumnName(
        value="vol_ma_10",
        full_name="Volume Moving Average (10)",
        description="The average of the last 10 volumes, highlighting typical trading activity.",
    )
    VOL_MA_20 = ColumnName(
        value="vol_ma_20",
        full_name="Volume Moving Average (20)",
        description="The average of the last 20 volumes, highlighting typical trading activity.",
    )
    VOL_MA_50 = ColumnName(
        value="vol_ma_50",
        full_name="Volume Moving Average (50)",
        description="The average of the last 50 volumes, highlighting typical trading activity.",
    )
    VOL_MA_100 = ColumnName(
        value="vol_ma_100",
        full_name="Volume Moving Average (100)",
        description="The average of the last 100 volumes, highlighting typical trading activity.",
    )
    VOL_MA_200 = ColumnName(
        value="vol_ma_200",
        full_name="Volume Moving Average (200)",
        description="The average of the last 200 volumes, highlighting typical trading activity.",
    )
    VOL_CHANGE = ColumnName(
        value="vol_change",
        full_name="Volume Change",
        description="The percent change in volume from the previous period, signaling unusual trading activity.",
    )
    VWAP_10 = ColumnName(
        value="vwap_10",
        full_name="Volume Weighted Average Price (10)",
        description="The rolling 10-period VWAP, reflecting average transaction price weighted by volume.",
    )
    VWAP_20 = ColumnName(
        value="vwap_20",
        full_name="Volume Weighted Average Price (20)",
        description="The rolling 20-period VWAP, reflecting average transaction price weighted by volume.",
    )
    VWAP_50 = ColumnName(
        value="vwap_50",
        full_name="Volume Weighted Average Price (50)",
        description="The rolling 50-period VWAP, reflecting average transaction price weighted by volume.",
    )
    VWAP_100 = ColumnName(
        value="vwap_100",
        full_name="Volume Weighted Average Price (100)",
        description="The rolling 100-period VWAP, reflecting average transaction price weighted by volume.",
    )
    VWAP_150 = ColumnName(
        value="vwap_150",
        full_name="Volume Weighted Average Price (150)",
        description="The rolling 150-period VWAP, reflecting average transaction price weighted by volume.",
    )
    VWAP_200 = ColumnName(
        value="vwap_200",
        full_name="Volume Weighted Average Price (200)",
        description="The rolling 200-period VWAP, reflecting average transaction price weighted by volume.",
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
    MOMENTUM_10 = ColumnName(
        value="momentum_10",
        full_name="Momentum (10)",
        description="The difference between the current close and the close 10 periods ago, measuring price momentum.",
    )
    ROC_10 = ColumnName(
        value="roc_10",
        full_name="Rate of Change (10)",
        description="The percent change in close price over the last 10 periods, measuring momentum.",
    )
    STOCHASTIC_K = ColumnName(
        value="stochastic_k",
        full_name="Stochastic Oscillator %K",
        description="The %K value of the stochastic oscillator, measuring the close's position relative to the recent high/low range.",
    )
    STOCHASTIC_D = ColumnName(
        value="stochastic_d",
        full_name="Stochastic Oscillator %D",
        description="The %D value (3-period SMA of %K) of the stochastic oscillator.",
    )
    BOLLINGER_UPPER = ColumnName(
        value="bollinger_upper",
        full_name="Bollinger Upper Band",
        description="The upper band of the Bollinger Bands (typically 2 std above the 20-period SMA).",
    )
    BOLLINGER_LOWER = ColumnName(
        value="bollinger_lower",
        full_name="Bollinger Lower Band",
        description="The lower band of the Bollinger Bands (typically 2 std below the 20-period SMA).",
    )
    BOLLINGER_WIDTH = ColumnName(
        value="bollinger_width",
        full_name="Bollinger Band Width",
        description="The width between the upper and lower Bollinger Bands, measuring volatility.",
    )
    GAP = ColumnName(
        value="gap",
        full_name="Price Gap",
        description="The difference between the current open and the previous close, indicating overnight or session gaps.",
    )
    HIGH_LOW_RATIO = ColumnName(
        value="high_low_ratio",
        full_name="High/Low Ratio",
        description="The ratio of the high price to the low price for the period, as a measure of volatility.",
    )
    OBV = ColumnName(
        value="obv",
        full_name="On-Balance Volume",
        description="A cumulative indicator that adds volume on up days and subtracts volume on down days, measuring buying/selling pressure.",
    )
    ADL = ColumnName(
        value="adl",
        full_name="Accumulation/Distribution Line",
        description="A volume-based indicator measuring the cumulative flow of money into and out of a security.",
    )
