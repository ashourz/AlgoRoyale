from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.data_preparer import DataPreparer


class DummyStage:
    required_input_columns = ["new", "bar"]


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def preparer(logger):
    return DataPreparer(logger)


def test_validate_dataframe_success(preparer):
    df = pd.DataFrame({"new": [1, 2], "bar": [3, 4]})
    stage = DummyStage()
    result = preparer.validate_dataframe(df, stage, "AAPL")
    assert list(result.columns) == ["new", "bar"]


def test_validate_dataframe_missing_column(preparer):
    df = pd.DataFrame({"new": [1, 2]})
    stage = DummyStage()
    with pytest.raises(ValueError) as excinfo:
        preparer.validate_dataframe(df, stage, "AAPL")
    assert "Missing columns" in str(excinfo.value)


def test_validate_dataframe_not_dataframe(preparer):
    stage = DummyStage()
    with pytest.raises(ValueError):
        preparer.validate_dataframe([1, 2, 3], stage, "AAPL")


def test_validate_dataframe_empty(preparer, logger):
    df = pd.DataFrame(columns=["new", "bar"])
    stage = DummyStage()
    result = preparer.validate_dataframe(df, stage, "AAPL")
    assert result.empty
    logger.debug.assert_called_with("Empty dataframe for AAPL")
