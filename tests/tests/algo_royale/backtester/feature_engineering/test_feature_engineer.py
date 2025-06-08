from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.mark.asyncio
async def test_engineer_features_yields_engineered(mock_logger):
    # Use a simple fake feature engineering function
    def fake_feature_engineering(df, logger=None):
        df = df.copy()
        df["engineered"] = 1
        return df

    async def df_iter():
        yield pd.DataFrame({"a": [1]})
        yield pd.DataFrame({"a": [2]})

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
async def test_engineer_features_handles_exception(capsys, mock_logger):
    # Use a feature engineering function that raises
    def bad_feature_engineering(df, logger=None):  # <-- Accept logger
        raise ValueError("bad data")

    async def df_iter():
        yield pd.DataFrame({"a": [1]})

    fe = FeatureEngineer(
        feature_engineering_func=bad_feature_engineering, logger=mock_logger
    )
    results = []
    async for df in fe.engineer_features(df_iter(), "AAPL"):
        results.append(df)

    # Should yield nothing, but print error
    assert results == []
    mock_logger.error.assert_any_call("Feature engineering failed for AAPL: bad data")
