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
    # Always return a real temp directory for file operations, including strategy_name
    mgr.get_directory_path.side_effect = (
        lambda stage, strategy_name, symbol: tmp_path
        / f"{stage}_{strategy_name}_{symbol}"
    )
    return mgr


@pytest.fixture
def writer(mock_logger, mock_stage_data_manager):
    from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter

    return StageDataWriter(
        logger=mock_logger,
        stage_data_manager=mock_stage_data_manager,
        max_rows_per_file=2,  # Small for chunking test
    )


def test_save_stage_data_creates_file(writer, tmp_path):
    """Test saving a small DataFrame creates a CSV file."""
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(stage, strategy_name, symbol, df)
    assert len(filepaths) == 1
    assert tmp_path in map(
        lambda f: Path(f).parent.parent, filepaths
    )  # parent.parent because of strategy_name in path


def test_save_stage_data_splits_large_df(writer):
    """Test large DataFrame is split into multiple files."""
    df = pd.DataFrame({"col1": range(5), "col2": range(5)})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(stage, strategy_name, symbol, df)
    assert len(filepaths) == 3  # 5 rows, 2 per file => 3 files


def test_save_stage_data_adds_columns(writer):
    """Test that strategy and symbol columns are added if missing."""
    df = pd.DataFrame({"col1": [1, 2]})
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    filepaths = writer.save_stage_data(stage, strategy_name, symbol, df)
    saved_df = pd.read_csv(filepaths[0])
    assert "strategy" in saved_df.columns
    assert "symbol" in saved_df.columns
    assert all(saved_df["strategy"] == strategy_name)
    assert all(saved_df["symbol"] == symbol)


def test_save_stage_data_none_df_raises(writer):
    """Test that passing None as DataFrame raises ValueError."""
    with pytest.raises(ValueError):
        writer.save_stage_data(BacktestStage.DATA_INGEST, "strat", "AAPL", None)


def test_save_stage_data_wrong_type_raises(writer):
    """Test that passing wrong type raises TypeError."""
    with pytest.raises(TypeError):
        writer.save_stage_data(BacktestStage.DATA_INGEST, "strat", "AAPL", [1, 2, 3])


def test_has_existing_results(writer, tmp_path):
    """Test has_existing_results returns True if file exists."""
    stage = BacktestStage.DATA_INGEST
    strategy_name = "strat"
    symbol = "AAPL"
    # Create a fake file in the correct directory structure
    dir_path = tmp_path / f"{stage}_{strategy_name}_{symbol}"
    dir_path.mkdir(parents=True, exist_ok=True)
    file = dir_path / f"{strategy_name}_{symbol}_123456.csv"
    file.write_text("col1,col2\n1,2\n")
    # Patch _get_stage_symbol_dir to use our temp dir with strategy_name
    writer._get_stage_symbol_dir = lambda stage, strategy_name, symbol: dir_path
    assert writer.has_existing_results(stage, strategy_name, symbol)
