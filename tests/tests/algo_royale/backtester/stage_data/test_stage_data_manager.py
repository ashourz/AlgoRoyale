import tempfile
from pathlib import Path

import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.backtester.stage_data.stage_data_manager import mockStageDataManager


# Create a temporary directory for testing
@pytest.fixture
def temp_stage_data_manager():
    temp_dir = tempfile.mkdtemp()
    return mockStageDataManager(
        data_dir=Path(temp_dir),
    )


def test_write_and_read_file(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "testfile",
        DataExtension.DONE,
        "hello",
    )
    content = mgr.read_file(
        BacktestStage.DATA_INGEST, None, "AAPL", "testfile", DataExtension.DONE
    )
    assert content == "hello"


def test_file_exists_and_delete(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "testfile",
        DataExtension.PROCESSED,
        "data",
    )
    assert mgr.file_exists(
        BacktestStage.DATA_INGEST, None, "AAPL", "testfile", DataExtension.PROCESSED
    )
    mgr.delete_file(
        BacktestStage.DATA_INGEST, None, "AAPL", "testfile", DataExtension.PROCESSED
    )
    assert not mgr.file_exists(
        BacktestStage.DATA_INGEST, None, "AAPL", "testfile", DataExtension.PROCESSED
    )


def test_mark_and_check_stage_done(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.mark_stage(BacktestStage.DATA_INGEST, DataExtension.DONE)
    assert mgr.is_stage_done(BacktestStage.DATA_INGEST)


def test_write_error_file(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_error_file(BacktestStage.DATA_INGEST, None, "AAPL", "errfile", "error!")
    dir_path = mgr.get_directory_path(stage=BacktestStage.DATA_INGEST, symbol="AAPL")
    error_file = dir_path / "errfile.error.csv"
    assert error_file.exists()
    assert error_file.read_text().strip() == "error!"


def test_get_file_path_and_directory_path(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    path = mgr.get_file_path(
        stage=BacktestStage.DATA_INGEST,
        strategy_name="strategy1",
        symbol="AAPL",
        filename="file",
        extension=DataExtension.UNPROCESSED,
    )
    assert "strategy1" in str(path)
    dir_path = mgr.get_directory_path(
        stage=BacktestStage.DATA_INGEST, strategy_name="strategy1", symbol="AAPL"
    )
    assert dir_path.name == "strategy1"


def test_get_stage_path_creates_dir(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    stage_path = mgr.get_stage_path(BacktestStage.DATA_INGEST)
    assert stage_path.exists()
    assert stage_path.is_dir()


def test_is_symbol_stage_done(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.mark_symbol_stage(BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.DONE)
    assert mgr.is_symbol_stage_done(BacktestStage.DATA_INGEST, None, "AAPL")


def test_mark_symbol_stage_removes_old_markers(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.mark_symbol_stage(BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.ERROR)
    mgr.mark_symbol_stage(BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.DONE)
    dir_path = mgr.get_directory_path(
        stage=BacktestStage.DATA_INGEST, strategy_name=None, symbol="AAPL"
    )
    files = list(dir_path.glob("*"))
    # Ensure only the DONE marker is present
    assert any(f.name.endswith(f"{DataExtension.DONE.value}.csv") for f in files)
    assert not any(
        f.name.endswith(f"{DataExtension.ERROR.value}.csv")
        for f in files
        if f.name != f"{BacktestStage.DATA_INGEST.value}.{DataExtension.DONE.value}.csv"
    )


def test_update_file_appends(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "testfile",
        DataExtension.PROCESSING,
        "foo",
    )
    mgr.update_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "testfile",
        DataExtension.PROCESSING,
        "bar",
    )
    content = mgr.read_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "testfile",
        DataExtension.PROCESSING,
    )
    assert content == "foobar"


def test_list_files(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "file1",
        DataExtension.UNPROCESSED,
        "a",
    )
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "file2",
        DataExtension.UNPROCESSED,
        "b",
    )
    files = mgr.list_files(BacktestStage.DATA_INGEST, None, "AAPL")
    file_names = [f.name for f in files]
    assert "file1.unprocessed.csv" in file_names
    assert "file2.unprocessed.csv" in file_names


def test_clear_directory(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST,
        None,
        "AAPL",
        "file1",
        DataExtension.PROCESSED,
        "a",
    )
    mgr.clear_directory(
        stage=BacktestStage.DATA_INGEST, strategy_name=None, symbol="AAPL"
    )
    dir_path = mgr.get_directory_path(
        stage=BacktestStage.DATA_INGEST, strategy_name=None, symbol="AAPL"
    )
    assert not dir_path.exists()


def test_clear_all_data(temp_stage_data_manager):
    mgr = temp_stage_data_manager
    mgr.write_file(
        BacktestStage.DATA_INGEST, None, "AAPL", "file1", DataExtension.DONE, "a"
    )
    mgr.clear_all_data()
    # Pass if the directory does not exist or is empty
    assert not mgr.base_dir.exists() or not any(mgr.base_dir.iterdir())
