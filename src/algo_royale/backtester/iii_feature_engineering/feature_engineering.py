import pandas as pd
import numpy as np

def feature_engineering(df):
    # Time features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    # Price returns
    df['pct_return'] = df['close_price'].pct_change()
    df['log_return'] = np.log(df['close_price']).diff()

    # Moving averages
    df['sma_20'] = df['close_price'].rolling(window=20).mean()
    df['ema_20'] = df['close_price'].ewm(span=20, adjust=False).mean()

    # Volatility
    df['volatility_20'] = df['pct_return'].rolling(window=20).std()

    # Range and candle features
    df['range'] = df['high_price'] - df['low_price']
    df['body'] = abs(df['close_price'] - df['open_price'])
    df['upper_wick'] = df['high_price'] - df[['open_price', 'close_price']].max(axis=1)
    df['lower_wick'] = df[['open_price', 'close_price']].min(axis=1) - df['low_price']

    # Volume features
    df['vol_ma_20'] = df['volume'].rolling(window=20).mean()
    df['vol_change'] = df['volume'].pct_change()

    # VWAP rolling
    df['vwap_20'] = (df['volume_weighted_price'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()

    # Drop NaN rows created by rolling calculations
    df = df.dropna().reset_index(drop=True)
    return df