from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.data_preparer.data_preparer import DataPreparer


class DummyStage:
    rename_map = {"old": "new", "foo": "bar"}
    required_input_columns = ["new", "bar"]


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def preparer(logger):
    return DataPreparer(logger)


def test_normalize_dataframe_success(preparer):
    df = pd.DataFrame({"old": [1, 2], "foo": [3, 4]})
    stage = DummyStage()
    result = preparer.normalize_dataframe(df, stage, "AAPL")
    assert list(result.columns) == ["new", "bar"]


def test_normalize_dataframe_missing_column(preparer):
    df = pd.DataFrame({"old": [1, 2]})
    stage = DummyStage()
    with pytest.raises(ValueError) as excinfo:
        preparer.normalize_dataframe(df, stage, "AAPL")
    assert "Missing columns" in str(excinfo.value)


def test_normalize_dataframe_not_dataframe(preparer):
    stage = DummyStage()
    with pytest.raises(ValueError):
        preparer.normalize_dataframe([1, 2, 3], stage, "AAPL")


def test_normalize_dataframe_empty(preparer, logger):
    df = pd.DataFrame(columns=["old", "foo"])
    stage = DummyStage()
    result = preparer.normalize_dataframe(df, stage, "AAPL")
    assert result.empty
    logger.debug.assert_called_with("Empty dataframe for AAPL")


def test_prepare_all_success(preparer):
    df = pd.DataFrame({"old": [1], "foo": [2]})
    stage = DummyStage()
    raw_data = {"AAPL": df}
    result = preparer.prepare_all(raw_data, stage)
    assert "AAPL" in result
    assert list(result["AAPL"].columns) == ["new", "bar"]


def test_prepare_all_handles_exception(preparer, logger):
    df = pd.DataFrame({"old": [1]})  # missing 'foo'
    stage = DummyStage()
    raw_data = {"AAPL": df}
    result = preparer.prepare_all(raw_data, stage)
    assert "AAPL" not in result
    logger.error.assert_called()
