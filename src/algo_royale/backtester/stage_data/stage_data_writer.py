import glob
from logging import Logger
from math import ceil
from pathlib import Path
from typing import Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_manager import (
    StageDataManager,
    mockStageDataManager,
)
from algo_royale.logging.logger_singleton import mockLogger


class StageDataWriter:
    """
    Class to save results from the pipeline stages to CSV files.
    It handles the creation of directories and file naming conventions.
    """

    def __init__(
        self,
        logger: Logger,
        stage_data_manager: StageDataManager,
        max_rows_per_file: int = 1_000_000,
    ):
        """
        Initialize the results saver with directory from config.
        """
        self.stage_data_manager = stage_data_manager
        self.max_rows_per_file = max_rows_per_file
        self.logger = logger

    def has_existing_results(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> bool:
        """
        Check if results already exist for the given stage, strategy, and symbol.
        This is useful to avoid overwriting existing results.
        """
        search_dir = self._get_stage_symbol_dir(
            stage, strategy_name, symbol, start_date, end_date
        )
        pattern = str(search_dir / f"{strategy_name}_{symbol}_*.csv")
        return len(glob.glob(pattern)) > 0

    def save_stage_data(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        results_df: pd.DataFrame,
        page_idx: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[str]:
        """
        Save the results DataFrame to CSV files, splitting if necessary.
        """
        if results_df is None:
            raise ValueError("None DataFrame provided")
        if not isinstance(results_df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(results_df)}")

        output_dir = self._get_stage_symbol_dir(
            stage, strategy_name, symbol, start_date, end_date
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        if strategy_name is not None and "strategy" not in results_df.columns:
            results_df = results_df.assign(strategy=strategy_name)
        if "symbol" not in results_df.columns:
            results_df = results_df.assign(symbol=symbol)

        total_rows = len(results_df)
        num_parts = ceil(total_rows / self.max_rows_per_file)
        filepaths = []

        for chunk_idx in range(num_parts):
            chunk_df = results_df.iloc[
                chunk_idx * self.max_rows_per_file : (chunk_idx + 1)
                * self.max_rows_per_file
            ]
            if num_parts > 1:
                filename = (
                    f"{strategy_name}_{symbol}_page{page_idx}_chunk{chunk_idx + 1}.csv"
                )
            else:
                filename = f"{strategy_name}_{symbol}_page{page_idx}.csv"
            filepath = output_dir / filename

            try:
                chunk_df.to_csv(filepath, index=False)
                self.logger.info(
                    f"Saved page{page_idx} chunk{chunk_idx + 1}/{num_parts} to {filepath}"
                )
                filepaths.append(str(filepath))
            except Exception as e:
                self.logger.error(
                    f"Failed to save page{page_idx} chunk{chunk_idx + 1} for {strategy_name}/{symbol}/{start_date}_{end_date}: {e}"
                )
                raise

        return filepaths

    def _get_stage_symbol_dir(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str],
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Path:
        """Get the directory for a symbol in the stage, optionally with strategy_name."""
        return self.stage_data_manager.get_directory_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )


def mockStageDataWriter(
    data_dir: Path,
) -> StageDataWriter:
    """
    Creates a mock StageDataWriter for testing purposes.
    """
    logger = mockLogger()
    stage_data_manager = mockStageDataManager(
        data_dir=data_dir,
        logger=logger,
    )
    return StageDataWriter(
        stage_data_manager=stage_data_manager,
        logger=logger,
    )
