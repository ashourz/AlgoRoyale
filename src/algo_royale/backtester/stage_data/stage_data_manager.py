import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.enums.data_extension import DataExtension
from algo_royale.logging.loggable import Loggable


class StageDataManager:
    """
    A class to manage data files for different pipeline stages and strategies.
    It provides methods to read, write, update, delete, and check the existence of files.
    It also provides methods to list files in a directory and clear directories.
    """

    def __init__(self, data_dir: str, logger: Loggable):
        self.base_dir = Path(data_dir)
        self.logger = logger

    def get_file_path(
        self,
        filename: str,
        extension: DataExtension,
        stage: Optional[BacktestStage] = None,
        symbol: Optional[str] = None,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Path:
        path = self.get_directory_path(
            stage=stage,
            symbol=symbol,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
        )
        path = path / f"{filename}.{extension.value}.csv"
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
        base_dir: Optional[Path] = None,
        stage: Optional[BacktestStage] = None,
        symbol: Optional[str] = None,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Path:
        """Generate the directory path for a given stage, strategy, and symbol.
        If base_dir is not provided, use the instance's base_dir.
        If stage, symbol, or strategy_name are not provided, they will be omitted from the path.
        If start_date and end_date are provided, a date window ID will be appended to the path.
        Directory structure:
        base_dir/<stage>/<symbol>/<strategy_name>/<date_window_id>/
        """
        if base_dir is None:
            base_dir = self.base_dir
        path = base_dir
        if stage:
            path = path / stage.name
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
        path = self.base_dir / stage.name
        path.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Ensured stage directory exists: {path}")
        return path

    def is_stage_done(self, stage: BacktestStage) -> bool:
        done_file = (
            self.get_stage_path(stage) / f"{stage.name}.{DataExtension.DONE.value}.csv"
        )
        exists = done_file.exists()
        self.logger.debug(f"Checked if stage done file exists ({done_file}): {exists}")
        return exists

    def is_symbol_stage_done(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        done_file = (
            self.get_directory_path(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            / f"{stage.name}.{DataExtension.DONE.value}.csv"
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
            marker_file = stage_path / f"{stage.name}.{ext.value}.csv"
            if marker_file.exists():
                marker_file.unlink()
                self.logger.info(f"Removed old marker file: {marker_file}")
        status_file = stage_path / f"{stage.name}.{statusExtension.value}.csv"
        status_file.touch()
        self.logger.info(f"Created new marker file: {status_file}")

    def mark_symbol_stage(
        self,
        stage: BacktestStage,
        symbol: str,
        statusExtension: DataExtension,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        stage_path = self.get_directory_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        stage_path.mkdir(parents=True, exist_ok=True)
        for ext in DataExtension:
            marker_file = stage_path / f"{stage.name}.{ext.value}.csv"
            if marker_file.exists():
                marker_file.unlink()
                self.logger.info(f"Removed old symbol marker file: {marker_file}")
        status_file = stage_path / f"{stage.name}.{statusExtension.value}.csv"
        status_file.touch()
        self.logger.info(f"Created new symbol marker file: {status_file}")

    def file_exists(
        self,
        stage: BacktestStage,
        symbol: str,
        filename: str,
        extension: DataExtension,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        path = self.get_file_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            filename=filename,
            extension=extension,
        )
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
        path = self.get_file_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            filename=filename,
            extension=extension,
        )
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
        path = self.get_file_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            filename=filename,
            extension=extension,
        )
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
        filename: str,
        error_message: str,
        strategy_name: Optional[str] = None,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        """Write an error message to a file in the specified stage and symbol directory."""
        dir_path = self.get_directory_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
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
        path = self.get_file_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            filename=filename,
            extension=extension,
        )
        if path.exists():
            os.remove(path)
            self.logger.info(f"Deleted file: {path}")
        else:
            self.logger.warning(f"Tried to delete non-existent file: {path}")

    def list_files(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> list:
        dir_path = self.get_directory_path(
            stage=stage, strategy_name=strategy_name, symbol=symbol
        )
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
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
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

    def dir_has_files(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        file_pattern: Optional[str] = None,
    ) -> bool:
        """Check if a directory has files matching a given pattern or any files if no pattern is provided."""
        dir_path = self.get_directory_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        if not dir_path.exists():
            self.logger.warning(f"Tried to check non-existent directory: {dir_path}")
            return False
        if not dir_path.is_dir():
            self.logger.warning(f"Tried to check a non-directory path: {dir_path}")
            return False
        if not dir_path.is_absolute():
            self.logger.warning(f"Path is not absolute: {dir_path}")
            return False
        # If a file pattern is provided, check if the directory has files matching the pattern
        if file_pattern:
            files = list(dir_path.glob(file_pattern))
            has_files = bool(files)
            self.logger.debug(
                f"Checked if directory has files matching pattern '{file_pattern}' ({dir_path}): {has_files}"
            )
            return has_files
        # If no pattern is provided, check if the directory has any files
        has_files = any(dir_path.iterdir())
        self.logger.debug(f"Checked if directory has files ({dir_path}): {has_files}")
        return has_files
