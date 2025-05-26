import os
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

    def __init__(self):
        self.base_dir = get_data_dir()

    def get_file_path(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> Path:
        if strategy_name:
            return (
                self.base_dir
                / stage.value
                / strategy_name
                / symbol
                / f"{filename}{extension.value}"
            )
        # If no strategy name is provided, use the symbol as the directory
        return self.base_dir / stage.value / symbol / f"{filename}{extension.value}"

    def get_directory_path(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> Path:
        if strategy_name:
            return self.base_dir / stage.value / strategy_name / symbol
        # If no strategy name is provided, use the symbol as the directory
        return self.base_dir / stage.value / symbol

    def get_stage_path(self, stage: BacktestStage) -> Path:
        path = self.base_dir / stage.value
        path.mkdir(parents=True, exist_ok=True)
        return path

    def is_stage_done(self, stage: BacktestStage) -> bool:
        done_file = (
            self.get_stage_path(stage) / f"{stage.value}{DataExtension.DONE.value}"
        )
        return done_file.exists()

    def is_symbol_stage_done(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> bool:
        if strategy_name:
            done_file = (
                self.get_directory_path(stage, strategy_name, symbol)
                / f"{stage.value}{DataExtension.DONE.value}"
            )
        else:
            # If no strategy name is provided, use the symbol as the directory
            done_file = (
                self.get_directory_path(stage, None, symbol)
                / f"{stage.value}{DataExtension.DONE.value}"
            )
        return done_file.exists()

    def mark_stage(self, stage: BacktestStage, statusExtension: DataExtension) -> None:
        stage_path = self.get_stage_path(stage)
        # Remove any existing marker files for this stage
        for ext in DataExtension:
            marker_file = stage_path / f"{stage.value}{ext.value}"
            if marker_file.exists():
                marker_file.unlink()
        # Create the new marker file
        status_file = stage_path / f"{stage.value}{statusExtension.value}"
        status_file.touch()

    def mark_symbol_stage(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        statusExtension: DataExtension,
    ) -> None:
        if strategy_name:
            stage_path = self.get_directory_path(stage, strategy_name, symbol)
        else:
            # If no strategy name is provided, use the symbol as the directory
            stage_path = self.get_directory_path(stage, None, symbol)
        # Remove any existing marker files for this stage
        for ext in DataExtension:
            marker_file = stage_path / f"{stage.value}{ext.value}"
            if marker_file.exists():
                marker_file.unlink()
        # Create the new marker file
        status_file = stage_path / f"{stage.value}{statusExtension.value}"
        status_file.touch()

    def file_exists(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> bool:
        if strategy_name:
            return self.get_file_path(
                stage, strategy_name, symbol, filename, extension
            ).exists()
        # If no strategy name is provided, use the symbol as the directory
        return self.get_file_path(stage, symbol, filename, extension).exists()

    def read_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
        mode: str = "r",
    ) -> Optional[str]:
        if strategy_name:
            path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        else:
            # If no strategy name is provided, use the symbol as the directory
            path = self.get_file_path(stage, symbol, filename, extension)
        # Check if the file exists before trying to read it
        if not path.exists():
            return None
        with open(path, mode) as f:
            return f.read()

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
        if strategy_name:
            path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        else:
            # If no strategy name is provided, use the symbol as the directory
            path = self.get_file_path(stage, symbol, filename, extension)
        # Ensure the directory exists
        if not path.parent.exists():
            # Create the directory if it doesn't exist
            # This will create all parent directories as well
            path.parent.mkdir(parents=True, exist_ok=True)
        # Write the data to the file
        with open(path, mode) as f:
            f.write(data)

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
        self.write_file(
            stage, strategy_name, symbol, filename, extension, data, mode=mode
        )

    def write_error_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        error_message: str,
    ) -> None:
        """
        Write an error message to a .error.txt file for the given stage, strategy, symbol, and filename.
        """
        if strategy_name:
            dir_path = self.get_directory_path(stage, strategy_name, symbol)
        else:
            dir_path = self.get_directory_path(stage, None, symbol)
        dir_path.mkdir(parents=True, exist_ok=True)
        error_file = dir_path / f"{filename}.{DataExtension.ERROR.value}.txt"
        with open(error_file, "w") as f:
            f.write(error_message)

    def delete_file(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        filename: str,
        extension: DataExtension,
    ) -> None:
        if strategy_name:
            path = self.get_file_path(stage, strategy_name, symbol, filename, extension)
        else:
            # If no strategy name is provided, use the symbol as the directory
            path = self.get_file_path(stage, symbol, filename, extension)
        # Check if the file exists before trying to delete it
        if path.exists():
            os.remove(path)

    def list_files(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> list:
        path = self.get_directory_path(stage, strategy_name, symbol)
        # List all files in the directory
        return [f for f in path.parent.iterdir() if f.is_file()]

    def clear_directory(
        self, stage: BacktestStage, strategy_name: Optional[str], symbol: str
    ) -> None:
        path = self.get_directory_path(stage, strategy_name, symbol)
        # Check if the directory exists before trying to clear it
        if not path.exists():
            return
        # Clear all files in the directory
        for f in path.parent.iterdir():
            if f.is_file():
                os.remove(f)
        # Optionally, remove the directory itself
        if path.parent.exists():
            os.rmdir(path.parent)

    def clear_all_data(self) -> None:
        # Clear all data in the base directory
        for item in self.base_dir.iterdir():
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                for f in item.iterdir():
                    if f.is_file():
                        os.remove(f)
                os.rmdir(item)
        # Optionally, remove the base directory itself
        if self.base_dir.exists():
            os.rmdir(self.base_dir)
