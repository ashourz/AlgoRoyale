import os
import shutil
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Any, Optional

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.utils.path_utils import get_data_dir


class StageDataManager:
    """
    A class to manage data files for different pipeline stages and strategies.
    It provides methods to read, write, update, delete, and check the existence of files.
    It also provides methods to list files in a directory and clear directories.
    """

    def __init__(self, logger: Logger):
        self.base_dir = get_data_dir()
        self.logger = logger

    def get_file_path(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> Path:
        path = (
            self.base_dir
            / stage.value
            / strategy_name
            / symbol
            / f"{filename}.{extension.value}.csv"
            if strategy_name
            else self.base_dir
            / stage.value
            / symbol
            / f"{filename}.{extension.value}.csv"
        )
        self.logger.debug(f"Generated file path: {path}")
        return path

    def get_window_id(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Generate a unique identifier for the date window."""
        if start_date and end_date:
            date_window_id = (
                f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            )
            self.logger.debug(f"Generated date window ID: {date_window_id}")
            return date_window_id
        else:
            raise ValueError("Start and end dates must be provided.")

    def get_directory_path(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: Optional[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Path:
        """Generate the directory path for a given stage, strategy, and symbol.
        If strategy_name is None, it will not include it in the path.
        If symbol is None, it will not include it in the path.
        """
        path = self.base_dir / stage.value
        if symbol:
            path = path / symbol
        if strategy_name:
            path = path / strategy_name
        if start_date and end_date:
            date_window_id = self.get_window_id(start_date, end_date)
            path = path / date_window_id

        self.logger.debug(f"Generated directory path: {path}")
        return path

    def get_extended_path(
        self,
        base_dir: str,
        strategy_name: Optional[str],
        symbol: Optional[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Path:
        """Generate the directory path for a given base directory, strategy, and symbol."""
        path = base_dir
        if symbol:
            path = path / symbol
        if strategy_name:
            path = path / strategy_name
        if start_date and end_date:
            date_window_id = self.get_window_id(start_date, end_date)
            path = path / date_window_id

        self.logger.debug(f"Generated directory path: {path}")
        return path

    def get_stage_path(self, stage: BacktestStage) -> Path:
        path = self.base_dir / stage.value
        path.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Ensured stage directory exists: {path}")
        return path

    def is_stage_done(self, stage: BacktestStage) -> bool:
        done_file = (
            self.get_stage_path(stage) / f"{stage.value}.{DataExtension.DONE.value}.csv"
        )
        exists = done_file.exists()
        self.logger.debug(f"Checked if stage done file exists ({done_file}): {exists}")
        return exists

    def is_symbol_stage_done(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        done_file = (
            self.get_directory_path(stage, strategy_name, symbol, start_date, end_date)
            / f"{stage.value}.{DataExtension.DONE.value}.csv"
        )
        exists = done_file.exists()
        self.logger.debug(
            f"Checked if symbol stage done file exists ({done_file}): {exists}"
        )
        return exists

    def mark_stage(self, stage: BacktestStage, statusExtension: DataExtension) -> None:
        stage_path = self.get_stage_path(stage)
        stage_path.mkdir(parents=True, exist_ok=True)
        for ext in DataExtension:
            marker_file = stage_path / f"{stage.value}.{ext.value}.csv"
            if marker_file.exists():
                marker_file.unlink()
                self.logger.info(f"Removed old marker file: {marker_file}")
        status_file = stage_path / f"{stage.value}.{statusExtension.value}.csv"
        status_file.touch()
        self.logger.info(f"Created new marker file: {status_file}")

    def mark_symbol_stage(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        statusExtension: DataExtension,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        stage_path = self.get_directory_path(
            stage, strategy_name, symbol, start_date, end_date
        )
        stage_path.mkdir(parents=True, exist_ok=True)
        for ext in DataExtension:
            marker_file = stage_path / f"{stage.value}.{ext.value}.csv"
            if marker_file.exists():
                marker_file.unlink()
                self.logger.info(f"Removed old symbol marker file: {marker_file}")
        status_file = stage_path / f"{stage.value}.{statusExtension.value}.csv"
        status_file.touch()
        self.logger.info(f"Created new symbol marker file: {status_file}")

    def file_exists(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> bool:
        path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        exists = path.exists()
        self.logger.debug(f"Checked if file exists ({path}): {exists}")
        return exists

    def read_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
        mode: str = "r",
    ) -> Optional[str]:
        path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        if not path.exists():
            self.logger.warning(f"Tried to read non-existent file: {path}")
            return None
        with open(path, mode) as f:
            data = f.read()
        self.logger.info(f"Read file: {path}")
        return data

    def write_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
        data: Any,
        mode: str = "w",
    ) -> None:
        path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory for writing file: {path.parent}")
        with open(path, mode) as f:
            f.write(data)
        self.logger.info(f"Wrote file: {path}")

    def update_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
        data: Any,
        mode: str = "a",
    ) -> None:
        self.logger.info(
            f"Updating file (append mode): {filename}.{extension.value}.csv"
        )
        self.write_file(
            stage, strategy_name, symbol, filename, extension, data, mode=mode
        )

    def write_error_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: Optional[str],
        filename: str,
        error_message: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        dir_path = self.get_directory_path(
            stage, strategy_name, symbol, start_date, end_date
        )
        dir_path.mkdir(parents=True, exist_ok=True)
        error_file = dir_path / f"{filename}.{DataExtension.ERROR.value}.csv"
        # Use append mode if file exists, else write mode
        mode = "a" if error_file.exists() else "w"
        with open(error_file, mode) as f:
            f.write(error_message)
            if not error_message.endswith("\n"):
                f.write("\n")
        self.logger.error(f"Wrote error file: {error_file}")

    def delete_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> None:
        path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        if path.exists():
            os.remove(path)
            self.logger.info(f"Deleted file: {path}")
        else:
            self.logger.warning(f"Tried to delete non-existent file: {path}")

    def list_files(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> list:
        dir_path = self.get_directory_path(stage, strategy_name, symbol)
        if not dir_path.exists():
            self.logger.warning(
                f"Tried to list files in non-existent directory: {dir_path}"
            )
            return []
        files = list(dir_path.glob("*"))
        self.logger.debug(f"Listed files in {dir_path}: {[f.name for f in files]}")
        return files

    def clear_directory(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        path = self.get_directory_path(
            stage, strategy_name, symbol, start_date, end_date
        )
        if not path.exists():
            self.logger.warning(f"Tried to clear non-existent directory: {path}")
            return
        for f in path.iterdir():
            if f.is_file():
                os.remove(f)
                self.logger.info(f"Deleted file in clear_directory: {f}")
        try:
            path.rmdir()
            self.logger.info(f"Removed directory: {path}")
        except OSError:
            self.logger.warning(
                f"Could not remove directory (not empty or error): {path}"
            )

    def clear_all_data(self) -> None:
        for item in self.base_dir.iterdir():
            if item.is_file():
                os.remove(item)
                self.logger.info(f"Deleted file in clear_all_data: {item}")
            elif item.is_dir():
                shutil.rmtree(item)
                self.logger.info(f"Removed subdirectory and all contents: {item}")
        try:
            self.base_dir.rmdir()
            self.logger.info(f"Removed base directory: {self.base_dir}")
        except OSError:
            self.logger.warning(
                f"Could not remove base directory (not empty or error): {self.base_dir}"
            )
