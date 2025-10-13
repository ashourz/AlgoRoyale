from pathlib import Path
from unittest.mock import MagicMock

from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from tests.mocks.mock_loggable import MockLoggable


class MockStageDataManager(StageDataManager):
    def __init__(self):
        super().__init__(data_dir=MagicMock(), logger=MockLoggable())
        self.file_path = "mocked_path"
        self.window_id = "mocked_window_id"
        self.return_false = False
        self.file_data = "mocked_file_data"
        self.return_none = False
        self.files = ["file1", "file2", "file3"]

    def set_return_false(self, value: bool):
        self.return_false = value

    def set_return_none(self, value: bool):
        self.return_none = value

    def reset_return_false(self):
        self.return_false = False

    def reset_return_none(self):
        self.return_none = False

    def reset(self):
        self.reset_return_false()
        self.reset_return_none()
        self.file_path = "mocked_path"
        self.window_id = "mocked_window_id"

    def get_file_path(
        self,
        filename,
        extension,
        stage=None,
        symbol=None,
        strategy_name=None,
        start_date=None,
        end_date=None,
    ):
        return Path(self.file_path)

    def get_window_id(self, start_date, end_date):
        return self.window_id

    def get_directory_path(
        self,
        base_dir=None,
        stage=None,
        symbol=None,
        strategy_name=None,
        start_date=None,
        end_date=None,
    ):
        return Path(self.file_path)

    def get_stage_path(self, stage):
        return Path(self.file_path)

    def is_stage_done(self, stage):
        if self.return_false:
            return False
        return True

    def mark_stage(self, stage, statusExtension):
        return None

    def mark_symbol_stage(
        self,
        stage,
        symbol,
        statusExtension,
        strategy_name=None,
        start_date=None,
        end_date=None,
    ):
        return None

    def file_exists(
        self,
        stage,
        symbol,
        filename,
        extension,
        strategy_name=None,
        start_date=None,
        end_date=None,
    ):
        if self.return_false:
            return False
        return True

    def read_file(self, stage, strategy_name, symbol, filename, extension, mode="r"):
        if self.return_none:
            return None
        return self.file_data

    def write_file(
        self,
        stage,
        strategy_name,
        symbol,
        filename,
        extension,
        content,
        start_date=None,
        end_date=None,
    ):
        return None

    def update_file(
        self, stage, strategy_name, symbol, filename, extension, data, mode="a"
    ):
        return None

    def write_error_file(
        self,
        stage,
        filename,
        error_message,
        strategy_name=None,
        symbol=None,
        start_date=None,
        end_date=None,
    ):
        return None

    def delete_file(
        self,
        stage,
        strategy_name,
        symbol,
        filename,
        extension,
        start_date=None,
        end_date=None,
    ):
        return None

    def list_files(self, stage, strategy_name, symbol):
        return self.files

    def clear_directory(
        self, stage, strategy_name, symbol, start_date=None, end_date=None
    ):
        return None

    def clear_all_data(self):
        return None

    def dir_has_files(
        self,
        stage,
        strategy_name,
        symbol,
        start_date=None,
        end_date=None,
        file_pattern=None,
    ):
        if self.return_false:
            return False
        return True
