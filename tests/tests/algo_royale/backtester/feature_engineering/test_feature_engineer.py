import numpy as np
import pandas as pd
import pytest

from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def sample_df():
    # 5 rows of fake OHLCV data
    return pd.DataFrame(
        {
            str(FeatureEngineeringColumns.CLOSE_PRICE): [100, 102, 101, 105, 110],
            str(FeatureEngineeringColumns.HIGH_PRICE): [101, 103, 102, 106, 111],
            str(FeatureEngineeringColumns.LOW_PRICE): [99, 101, 100, 104, 109],
        }
    )


def test_compute_max_lookback(monkeypatch):
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    monkeypatch.setattr(
        FeatureEngineeringColumns, "get_max_lookback_from_columns", lambda: 42
    )
    assert fe.compute_max_lookback() == 42


def test_compute_pct_return(sample_df):
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    result = fe._compute_pct_return(sample_df)
    expected = (110 - 105) / 105
    assert np.isclose(result, expected)


def test_compute_pct_return_too_short():
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    df = pd.DataFrame({str(FeatureEngineeringColumns.CLOSE_PRICE): [100]})
    result = fe._compute_pct_return(df)
    assert np.isnan(result)


def test_compute_log_return(sample_df):
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    result = fe._compute_log_return(sample_df)
    expected = np.log(110) - np.log(105)
    assert np.isclose(result, expected)


def test_compute_log_return_too_short():
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    df = pd.DataFrame({str(FeatureEngineeringColumns.CLOSE_PRICE): [100]})
    result = fe._compute_log_return(df)
    assert np.isnan(result)


def test_compute_sma(sample_df):
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    result = fe._compute_sma(sample_df, 3)
    expected = np.mean([101, 105, 110])
    assert np.isclose(result, expected)


def test_compute_sma_too_short():
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    df = pd.DataFrame({str(FeatureEngineeringColumns.CLOSE_PRICE): [100, 101]})
    result = fe._compute_sma(df, 3)
    assert np.isnan(result)


def test_compute_ema(sample_df):
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    result = fe._compute_ema(sample_df, 3)
    # Compare to pandas result
    expected = (
        sample_df[str(FeatureEngineeringColumns.CLOSE_PRICE)]
        .ewm(span=3, adjust=False)
        .mean()
        .iloc[-1]
    )
    assert np.isclose(result, expected)


def test_compute_ema_too_short():
    logger = MockLoggable()
    fe = FeatureEngineer(logger)
    df = pd.DataFrame({str(FeatureEngineeringColumns.CLOSE_PRICE): [100, 101]})
    result = fe._compute_ema(df, 3)
    assert np.isnan(result)
