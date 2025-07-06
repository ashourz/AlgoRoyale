from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.mark.asyncio
async def test_engineer_features_yields_engineered(mock_logger):
    # Use a fake feature engineering function that adds all expected columns
    def fake_feature_engineering(df, logger=mock_logger):
        df = df.copy()
        # Add all expected columns with dummy values
        expected_columns = [
            "adl",
            "adx",
            "atr_14",
            "body",
            "bollinger_lower",
            "bollinger_upper",
            "bollinger_width",
            "close_price",
            "day_of_week",
            "ema_10",
            "ema_100",
            "ema_12",
            "ema_150",
            "ema_20",
            "ema_200",
            "ema_26",
            "ema_50",
            "ema_9",
            "gap",
            "high_low_ratio",
            "high_price",
            "hist_volatility_20",
            "hour",
            "log_return",
            "lower_wick",
            "low_price",
            "macd",
            "macd_signal",
            "momentum_10",
            "num_trades",
            "obv",
            "open_price",
            "pct_return",
            "range",
            "roc_10",
            "rsi",
            "sma_10",
            "sma_100",
            "sma_150",
            "sma_20",
            "sma_200",
            "sma_50",
            "stochastic_d",
            "stochastic_k",
            "symbol",
            "timestamp",
            "upper_wick",
            "volatility_10",
            "volatility_20",
            "volatility_50",
            "volume",
            "volume_weighted_price",
            "vol_change",
            "vol_ma_10",
            "vol_ma_100",
            "vol_ma_20",
            "vol_ma_200",
            "vol_ma_50",
            "vwap_10",
            "vwap_100",
            "vwap_150",
            "vwap_20",
            "vwap_200",
            "vwap_50",
            "engineered",
        ]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0  # Add dummy values for missing columns
        return df

    async def df_iter():
        yield pd.DataFrame(
            {
                "close_price": [1],
                "high_price": [2],
                "low_price": [3],
                "num_trades": [4],
                "open_price": [5],
                "symbol": ["AAPL"],
                "timestamp": ["2025-07-06"],
                "volume": [100],
                "volume_weighted_price": [101],
            }
        )
        yield pd.DataFrame(
            {
                "close_price": [6],
                "high_price": [7],
                "low_price": [8],
                "num_trades": [9],
                "open_price": [10],
                "symbol": ["AAPL"],
                "timestamp": ["2025-07-07"],
                "volume": [200],
                "volume_weighted_price": [201],
            }
        )

    fe = FeatureEngineer(
        feature_engineering_func=fake_feature_engineering,
        logger=mock_logger,
        max_lookback=0,
    )
    results = []
    async for df in fe.engineer_features(df_iter(), "AAPL"):
        results.append(df)

    assert len(results) == 2
    assert all("engineered" in df.columns for df in results)


@pytest.mark.asyncio
async def test_engineer_features_handles_exception(mock_logger):
    # Use a feature engineering function that raises
    def bad_feature_engineering(df, logger=mock_logger):
        raise ValueError("bad data")

    async def df_iter():
        yield pd.DataFrame(
            {
                "close_price": [1],
                "high_price": [2],
                "low_price": [3],
                "num_trades": [4],
                "open_price": [5],
                "symbol": ["AAPL"],
                "timestamp": ["2025-07-06"],
                "volume": [100],
                "volume_weighted_price": [101],
            }
        )

    fe = FeatureEngineer(
        feature_engineering_func=bad_feature_engineering,
        logger=mock_logger,
    )
    results = []
    async for df in fe.engineer_features(df_iter(), "AAPL"):
        results.append(df)

    # Should yield nothing, but print error
    assert results == []
    mock_logger.error.assert_any_call("Feature engineering failed for AAPL: bad data")
