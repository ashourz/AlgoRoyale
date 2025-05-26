import numpy as np
import pandas as pd

from .feature_names import FeatureName


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    # Time features
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df[FeatureName.HOUR.value.value] = df["timestamp"].dt.hour
    df[FeatureName.DAY_OF_WEEK.value.value] = df["timestamp"].dt.dayofweek

    # Price returns
    df[FeatureName.PCT_RETURN.value.value] = df["close_price"].pct_change()
    df[FeatureName.LOG_RETURN.value.value] = np.log(df["close_price"]).diff()

    # Moving averages
    df[FeatureName.SMA_20.value.value] = df["close_price"].rolling(window=20).mean()
    df[FeatureName.EMA_20.value.value] = (
        df["close_price"].ewm(span=20, adjust=False).mean()
    )

    # Volatility
    df[FeatureName.VOLATILITY_20.value.value] = (
        df[FeatureName.PCT_RETURN.value.value].rolling(window=20).std()
    )

    # Range and candle features
    df[FeatureName.RANGE.value.value] = df["high_price"] - df["low_price"]
    df[FeatureName.BODY.value.value] = abs(df["close_price"] - df["open_price"])
    df[FeatureName.UPPER_WICK.value.value] = df["high_price"] - df[
        ["open_price", "close_price"]
    ].max(axis=1)
    df[FeatureName.LOWER_WICK.value.value] = (
        df[["open_price", "close_price"]].min(axis=1) - df["low_price"]
    )

    # Volume features
    df[FeatureName.VOL_MA_20.value.value] = df["volume"].rolling(window=20).mean()
    df[FeatureName.VOL_CHANGE.value.value] = df["volume"].pct_change()

    # VWAP rolling
    df[FeatureName.VWAP_20.value.value] = (
        df["volume_weighted_price"] * df["volume"]
    ).rolling(20).sum() / df["volume"].rolling(20).sum()

    # Drop NaN rows created by rolling calculations
    df = df.dropna().reset_index(drop=True)

    # Validation: ensure all features in FeatureName are present
    missing = [f.value.value for f in FeatureName if f.value.value not in df.columns]
    if missing:
        raise ValueError(f"Missing features after engineering: {missing}")

    return df
