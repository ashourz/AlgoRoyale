import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def asset_matrix_preparer():
    preparer = AssetMatrixPreparer(
        logger=MockLoggable(),
    )
    yield preparer


class TestAssetMatrixPreparer:
    def test_prepare_single_symbol(self, asset_matrix_preparer: AssetMatrixPreparer):
        df = pd.DataFrame(
            {
                "timestamp": [1, 2, 3],
                "close": [10, 11, 12],
            }
        )
        result = asset_matrix_preparer.prepare(
            df, symbol_col="symbol", timestamp_col="timestamp"
        )
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["close"]
        assert result.shape == (3, 1)

    def test_prepare_multi_symbol_value_col(
        self, asset_matrix_preparer: AssetMatrixPreparer
    ):
        df = pd.DataFrame(
            {
                "timestamp": [1, 1, 2, 2],
                "symbol": ["A", "B", "A", "B"],
                "feature": [0.1, 0.2, 0.3, 0.4],
            }
        )
        result = asset_matrix_preparer.prepare(
            df, value_col="feature", symbol_col="symbol", timestamp_col="timestamp"
        )
        assert isinstance(result, pd.DataFrame)
        assert set(result.columns) == {"A", "B"}
        assert result.shape == (2, 2)

    def test_prepare_multi_symbol_price_cols(
        self, asset_matrix_preparer: AssetMatrixPreparer
    ):
        df = pd.DataFrame(
            {
                "timestamp": [1, 1, 2, 2],
                "symbol": ["A", "B", "A", "B"],
                "close_price": [10, 20, 11, 21],
                "open_price": [9, 19, 10, 20],
                "high_price": [11, 21, 12, 22],
                "low_price": [8, 18, 9, 19],
            }
        )
        result = asset_matrix_preparer.prepare(
            df, symbol_col="symbol", timestamp_col="timestamp"
        )
        assert isinstance(result, pd.DataFrame)
        assert isinstance(result.columns, pd.MultiIndex)
        assert set(result.columns.get_level_values(1)) == {"A", "B"}
        assert set(result.columns.get_level_values(0)).issuperset(
            {"close_price", "open_price", "high_price", "low_price"}
        )
        assert result.shape == (2, 8)

    def test_prepare_no_price_cols(self, asset_matrix_preparer: AssetMatrixPreparer):
        df = pd.DataFrame(
            {
                "timestamp": [1, 2],
                "symbol": ["A", "B"],
                "foo": [1, 2],
            }
        )
        result = asset_matrix_preparer.prepare(
            df, symbol_col="symbol", timestamp_col="timestamp"
        )
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_prepare_missing_symbol_col(
        self, asset_matrix_preparer: AssetMatrixPreparer
    ):
        df = pd.DataFrame(
            {
                "timestamp": [1, 2, 3],
                "close": [10, 11, 12],
            }
        )
        result = asset_matrix_preparer.prepare(
            df, symbol_col="not_a_symbol", timestamp_col="timestamp"
        )
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["close"]
        assert result.shape == (3, 1)
