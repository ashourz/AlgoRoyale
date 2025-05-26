import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager


@pytest.fixture
def temp_stage_data_manager():
    # Create a temporary directory for testing
    @pytest.fixture
    def temp_stage_data_manager():
        temp_dir = tempfile.mkdtemp()
        with patch(
            "algo_royale.backtester.stage_data.stage_data_manager.get_data_dir",
            return_value=Path(temp_dir),
        ):
            manager = StageDataManager()
            yield manager
        shutil.rmtree(temp_dir)

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
        mgr.write_error_file(
            BacktestStage.DATA_INGEST, None, "AAPL", "errfile", "error!"
        )
        dir_path = mgr.get_directory_path(BacktestStage.DATA_INGEST, None, "AAPL")
        error_file = dir_path / "errfile.error.txt"
        assert error_file.exists()
        assert error_file.read_text() == "error!"

    def test_get_file_path_and_directory_path(temp_stage_data_manager):
        mgr = temp_stage_data_manager
        path = mgr.get_file_path(
            BacktestStage.DATA_INGEST,
            "strategy1",
            "AAPL",
            "file",
            DataExtension.UNPROCESSED,
        )
        assert "strategy1" in str(path)
        dir_path = mgr.get_directory_path(
            BacktestStage.DATA_INGEST, "strategy1", "AAPL"
        )
        assert dir_path.name == "AAPL"

    def test_get_stage_path_creates_dir(temp_stage_data_manager):
        mgr = temp_stage_data_manager
        stage_path = mgr.get_stage_path(BacktestStage.DATA_INGEST)
        assert stage_path.exists()
        assert stage_path.is_dir()

    def test_is_symbol_stage_done(temp_stage_data_manager):
        mgr = temp_stage_data_manager
        mgr.mark_symbol_stage(
            BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.DONE
        )
        assert mgr.is_symbol_stage_done(BacktestStage.DATA_INGEST, None, "AAPL")

    def test_mark_symbol_stage_removes_old_markers(temp_stage_data_manager):
        mgr = temp_stage_data_manager
        mgr.mark_symbol_stage(
            BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.ERROR
        )
        mgr.mark_symbol_stage(
            BacktestStage.DATA_INGEST, None, "AAPL", DataExtension.DONE
        )
        dir_path = mgr.get_directory_path(BacktestStage.DATA_INGEST, None, "AAPL")
        files = list(dir_path.glob("*"))
        assert any(f.name.endswith(DataExtension.DONE.value) for f in files)
        assert not any(
            f.name.endswith(DataExtension.ERROR.value)
            for f in files
            if f.name != f"{BacktestStage.DATA_INGEST.value}{DataExtension.DONE.value}"
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
        assert any("file1" in str(f) for f in files)
        assert any("file2" in str(f) for f in files)

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
        mgr.clear_directory(BacktestStage.DATA_INGEST, None, "AAPL")
        dir_path = mgr.get_directory_path(BacktestStage.DATA_INGEST, None, "AAPL")
        assert not any(dir_path.parent.iterdir())

    def test_clear_all_data(temp_stage_data_manager):
        mgr = temp_stage_data_manager
        mgr.write_file(
            BacktestStage.DATA_INGEST, None, "AAPL", "file1", DataExtension.DONE, "a"
        )
        mgr.clear_all_data()
        assert not any(mgr.base_dir.iterdir())
