from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_stage_data_manager(tmp_path):
    mgr = MagicMock()
    mgr.get_directory_path.side_effect = (
        lambda stage, strategy_name, symbol, start_date=None, end_date=None: tmp_path
        / f"{stage}_{strategy_name}_{symbol}"
    )
    return mgr


@pytest.fixture
def writer(mock_logger, mock_stage_data_manager):
    from algo_royale.backtester.stage_data.writer.stage_data_writer import (
        StageDataWriter,
    )

    return StageDataWriter(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        max_rows_per_file=2,  # Small for chunking test
    )


def test_save_stage_data_creates_file(writer, tmp_path):
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(
        stage, strategy_name, symbol, df, 1
    )  # <-- add page_idx
    assert len(filepaths) == 1
    assert tmp_path in map(lambda f: Path(f).parent.parent, filepaths)


def test_save_stage_data_splits_large_df(writer):
    df = pd.DataFrame({"col1": range(5), "col2": range(5)})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(
        stage, strategy_name, symbol, df, 1
    )  # <-- add page_idx
    assert len(filepaths) == 3


def test_save_stage_data_adds_columns(writer):
    df = pd.DataFrame({"col1": [1, 2]})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(
        stage, strategy_name, symbol, df, 1
    )  # <-- add page_idx
    saved_df = pd.read_csv(filepaths[0])
    assert "strategy" in saved_df.columns
    assert "symbol" in saved_df.columns
    assert all(saved_df["strategy"] == strategy_name)
    assert all(saved_df["symbol"] == symbol)


def test_save_stage_data_none_df_raises(writer):
    with pytest.raises(ValueError):
        writer.save_stage_data(
            BacktestStage.DATA_INGEST, "strat", "AAPL", None, 1
        )  # <-- add page_idx


def test_save_stage_data_wrong_type_raises(writer):
    with pytest.raises(TypeError):
        writer.save_stage_data(
            BacktestStage.DATA_INGEST, "strat", "AAPL", [1, 2, 3], 1
        )  # <-- add page_idx
