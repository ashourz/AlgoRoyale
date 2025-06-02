import numpy as np
import pandas as pd

from algo_royale.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


def feature_engineering(df: pd.DataFrame, logger) -> pd.DataFrame:
    logger.info(f"Input DataFrame shape: {df.shape}, columns: {list(df.columns)}")

    # Price returns
    df[FeatureEngineeringColumns.PCT_RETURN] = df[
        FeatureEngineeringColumns.CLOSE_PRICE
    ].pct_change()
    df[FeatureEngineeringColumns.LOG_RETURN] = np.log(
        df[FeatureEngineeringColumns.CLOSE_PRICE]
    ).diff()

    # Moving averages (loop for brevity)
    for window in [10, 20, 50, 100, 150, 200]:
        df[getattr(FeatureEngineeringColumns, f"SMA_{window}")] = (
            df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=window).mean()
        )
    for window in [9, 10, 12, 20, 26, 50, 100]:
        df[getattr(FeatureEngineeringColumns, f"EMA_{window}")] = (
            df[FeatureEngineeringColumns.CLOSE_PRICE]
            .ewm(span=window, adjust=False)
            .mean()
        )

    # MACD
    df[FeatureEngineeringColumns.MACD] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].ewm(span=12, adjust=False).mean()
        - df[FeatureEngineeringColumns.CLOSE_PRICE].ewm(span=26, adjust=False).mean()
    )

    # RSI
    df[FeatureEngineeringColumns.RSI] = calculate_rsi(
        df[FeatureEngineeringColumns.CLOSE_PRICE]
    )

    # Volatility
    for window in [10, 20, 50]:
        df[getattr(FeatureEngineeringColumns, f"VOLATILITY_{window}")] = (
            df[FeatureEngineeringColumns.PCT_RETURN].rolling(window=window).std()
        )
    df[FeatureEngineeringColumns.HIST_VOLATILITY_20] = df[
        FeatureEngineeringColumns.PCT_RETURN
    ].rolling(window=20).std() * np.sqrt(252)

    # ATR
    df[FeatureEngineeringColumns.ATR_14] = calculate_atr(df, window=14)

    # Range and candle features
    df[FeatureEngineeringColumns.RANGE] = (
        df[FeatureEngineeringColumns.HIGH_PRICE]
        - df[FeatureEngineeringColumns.LOW_PRICE]
    )
    df[FeatureEngineeringColumns.BODY] = abs(
        df[FeatureEngineeringColumns.CLOSE_PRICE]
        - df[FeatureEngineeringColumns.OPEN_PRICE]
    )
    df[FeatureEngineeringColumns.UPPER_WICK] = df[
        FeatureEngineeringColumns.HIGH_PRICE
    ] - df[
        [FeatureEngineeringColumns.OPEN_PRICE, FeatureEngineeringColumns.CLOSE_PRICE]
    ].max(axis=1)
    df[FeatureEngineeringColumns.LOWER_WICK] = (
        df[
            [
                FeatureEngineeringColumns.OPEN_PRICE,
                FeatureEngineeringColumns.CLOSE_PRICE,
            ]
        ].min(axis=1)
        - df[FeatureEngineeringColumns.LOW_PRICE]
    )

    # Volume features
    for window in [10, 20, 50, 100, 200]:
        df[getattr(FeatureEngineeringColumns, f"VOL_MA_{window}")] = (
            df[FeatureEngineeringColumns.VOLUME].rolling(window=window).mean()
        )
    df[FeatureEngineeringColumns.VOL_CHANGE] = df[
        FeatureEngineeringColumns.VOLUME
    ].pct_change()

    # VWAP rolling
    df[FeatureEngineeringColumns.VWAP_10] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(10).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(10).sum()
    df[FeatureEngineeringColumns.VWAP_20] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(20).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(20).sum()
    df[FeatureEngineeringColumns.VWAP_50] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(50).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(50).sum()
    df[FeatureEngineeringColumns.VWAP_100] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(100).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(100).sum()
    df[FeatureEngineeringColumns.VWAP_150] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(150).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(150).sum()
    df[FeatureEngineeringColumns.VWAP_200] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(200).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(200).sum()

    # Time features
    df[FeatureEngineeringColumns.HOUR] = df[FeatureEngineeringColumns.TIMESTAMP].dt.hour
    df[FeatureEngineeringColumns.DAY_OF_WEEK] = df[
        FeatureEngineeringColumns.TIMESTAMP
    ].dt.dayofweek

    # ADX
    df[FeatureEngineeringColumns.ADX] = calculate_adx(df, window=14)

    # Momentum, ROC
    df[FeatureEngineeringColumns.MOMENTUM_10] = df[
        FeatureEngineeringColumns.CLOSE_PRICE
    ] - df[FeatureEngineeringColumns.CLOSE_PRICE].shift(10)
    df[FeatureEngineeringColumns.ROC_10] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE]
        - df[FeatureEngineeringColumns.CLOSE_PRICE].shift(10)
    ) / df[FeatureEngineeringColumns.CLOSE_PRICE].shift(10)

    # Stochastic K/D
    low_14 = df[FeatureEngineeringColumns.LOW_PRICE].rolling(window=14).min()
    high_14 = df[FeatureEngineeringColumns.HIGH_PRICE].rolling(window=14).max()
    df[FeatureEngineeringColumns.STOCHASTIC_K] = (
        (df[FeatureEngineeringColumns.CLOSE_PRICE] - low_14) / (high_14 - low_14) * 100
    )
    df[FeatureEngineeringColumns.STOCHASTIC_D] = (
        df[FeatureEngineeringColumns.STOCHASTIC_K].rolling(window=3).mean()
    )

    # Bollinger Bands
    ma20 = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=20).mean()
    std20 = df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=20).std()
    df[FeatureEngineeringColumns.BOLLINGER_UPPER] = ma20 + 2 * std20
    df[FeatureEngineeringColumns.BOLLINGER_LOWER] = ma20 - 2 * std20
    df[FeatureEngineeringColumns.BOLLINGER_WIDTH] = (
        df[FeatureEngineeringColumns.BOLLINGER_UPPER]
        - df[FeatureEngineeringColumns.BOLLINGER_LOWER]
    ) / ma20

    # GAP, High/Low Ratio
    df[FeatureEngineeringColumns.GAP] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE]
        - df[FeatureEngineeringColumns.OPEN_PRICE]
    ) / df[FeatureEngineeringColumns.OPEN_PRICE]
    df[FeatureEngineeringColumns.HIGH_LOW_RATIO] = (
        df[FeatureEngineeringColumns.HIGH_PRICE]
        / df[FeatureEngineeringColumns.LOW_PRICE]
    ).replace([np.inf, -np.inf], np.nan)

    # OBV
    df[FeatureEngineeringColumns.OBV] = (
        (
            df[FeatureEngineeringColumns.VOLUME]
            * np.sign(df[FeatureEngineeringColumns.CLOSE_PRICE].diff())
        )
        .fillna(0)
        .cumsum()
    )

    # ADL
    df[FeatureEngineeringColumns.ADL] = (
        (
            df[FeatureEngineeringColumns.VOLUME]
            * (
                df[FeatureEngineeringColumns.CLOSE_PRICE]
                - df[FeatureEngineeringColumns.LOW_PRICE]
            )
            / (
                df[FeatureEngineeringColumns.HIGH_PRICE]
                - df[FeatureEngineeringColumns.LOW_PRICE]
            )
        ).fillna(0)
    ).cumsum()

    # Ensure timestamp is datetime
    df[FeatureEngineeringColumns.TIMESTAMP] = pd.to_datetime(
        df[FeatureEngineeringColumns.TIMESTAMP]
    )

    logger.info(f"DataFrame shape before dropna: {df.shape}")
    logger.info(f"DataFrame columns after feature engineering: {list(df.columns)}")

    # Validation: ensure all features in FeatureEngineeringColumns are present
    missing = [f for f in FeatureEngineeringColumns if f not in df.columns]
    if missing:
        logger.error(f"Missing features after engineering: {missing}")
        raise ValueError(f"Missing features after engineering: {missing}")

    logger.info(f"Feature engineering complete. Output shape: {df.shape}")
    return df


def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_atr(df, window=14):
    high = df[FeatureEngineeringColumns.HIGH_PRICE]
    low = df[FeatureEngineeringColumns.LOW_PRICE]
    close = df[FeatureEngineeringColumns.CLOSE_PRICE]
    tr = pd.concat(
        [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1
    ).max(axis=1)
    return tr.rolling(window=window, min_periods=window).mean()


def calculate_adx(df, window=14):
    high = df[FeatureEngineeringColumns.HIGH_PRICE]
    low = df[FeatureEngineeringColumns.LOW_PRICE]
    close = df[FeatureEngineeringColumns.CLOSE_PRICE]
    plus_dm = high.diff()
    minus_dm = low.diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window, min_periods=window).mean()
    plus_di = 100 * (plus_dm.rolling(window=window, min_periods=window).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=window, min_periods=window).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=window, min_periods=window).mean()
    return adx
