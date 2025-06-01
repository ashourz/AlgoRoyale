from logging import Logger

import numpy as np
import pandas as pd

from algo_royale.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)


def feature_engineering(df: pd.DataFrame, logger: Logger) -> pd.DataFrame:
    logger.info(f"Input DataFrame shape: {df.shape}, columns: {list(df.columns)}")

    # Time features
    df[FeatureEngineeringColumns.TIMESTAMP] = pd.to_datetime(
        df[FeatureEngineeringColumns.TIMESTAMP]
    )
    df[FeatureEngineeringColumns.HOUR] = df[FeatureEngineeringColumns.TIMESTAMP].dt.hour
    df[FeatureEngineeringColumns.DAY_OF_WEEK] = df[
        FeatureEngineeringColumns.TIMESTAMP
    ].dt.dayofweek

    # Price returns
    df[FeatureEngineeringColumns.PCT_RETURN] = df[
        FeatureEngineeringColumns.CLOSE_PRICE
    ].pct_change()
    df[FeatureEngineeringColumns.LOG_RETURN] = np.log(
        df[FeatureEngineeringColumns.CLOSE_PRICE]
    ).diff()

    df[FeatureEngineeringColumns.MACD] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].ewm(span=12, adjust=False).mean()
        - df[FeatureEngineeringColumns.CLOSE_PRICE].ewm(span=26, adjust=False).mean()
    )

    df[FeatureEngineeringColumns.RSI] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE]
        .diff()
        .rolling(window=14)
        .apply(
            lambda x: 100
            - (
                100
                / (1 + np.mean(np.where(x > 0, x, 0)) / np.mean(np.where(x < 0, -x, 0)))
            )
        )
    )
    df[FeatureEngineeringColumns.ADX] = df[
        FeatureEngineeringColumns.HIGH_PRICE
    ].rolling(window=14).apply(lambda x: np.mean(np.abs(np.diff(x)))) / df[
        FeatureEngineeringColumns.LOW_PRICE
    ].rolling(window=14).apply(lambda x: np.mean(np.abs(np.diff(x))))
    # Moving averages
    df[FeatureEngineeringColumns.SMA_20] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=20).mean()
    )
    df[FeatureEngineeringColumns.SMA_50] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=50).mean()
    )
    df[FeatureEngineeringColumns.SMA_200] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].rolling(window=200).mean()
    )
    df[FeatureEngineeringColumns.EMA_20] = (
        df[FeatureEngineeringColumns.CLOSE_PRICE].ewm(span=20, adjust=False).mean()
    )

    # Volatility
    df[FeatureEngineeringColumns.VOLATILITY_20] = (
        df[FeatureEngineeringColumns.PCT_RETURN].rolling(window=20).std()
    )

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
    df[FeatureEngineeringColumns.VOL_MA_20] = (
        df[FeatureEngineeringColumns.VOLUME].rolling(window=20).mean()
    )
    df[FeatureEngineeringColumns.VOL_CHANGE] = df[
        FeatureEngineeringColumns.VOLUME
    ].pct_change()

    # VWAP rolling
    df[FeatureEngineeringColumns.VWAP_20] = (
        df[FeatureEngineeringColumns.VOLUME_WEIGHTED_PRICE]
        * df[FeatureEngineeringColumns.VOLUME]
    ).rolling(20).sum() / df[FeatureEngineeringColumns.VOLUME].rolling(20).sum()

    logger.info(f"DataFrame shape before dropna: {df.shape}")
    logger.info(f"DataFrame columns after feature engineering: {list(df.columns)}")

    # Validation: ensure all features in FeatureEngineeringColumns are present
    missing = [f for f in FeatureEngineeringColumns if f not in df.columns]
    if missing:
        logger.error(f"Missing features after engineering: {missing}")
        raise ValueError(f"Missing features after engineering: {missing}")

    logger.info(f"Feature engineering complete. Output shape: {df.shape}")
    return df
