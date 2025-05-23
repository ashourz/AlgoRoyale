import glob
from datetime import datetime
from logging import Logger
from math import ceil
from pathlib import Path
from typing import Optional

import pandas as pd

from algo_royale.backtester.pipeline.data_manage import PipelineDataManager
from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage


class StageDataWriter:
    """
    Class to save results from the pipeline stages to CSV files.
    It handles the creation of directories and file naming conventions.
    """

    def __init__(
        self,
        logger: Logger,
        pipeline_data_manager: PipelineDataManager,
        max_rows_per_file: int = 1_000_000,
    ):
        """
        Initialize the results saver with directory from config.
        """
        self.pipeline_data_manager = pipeline_data_manager
        self.max_rows_per_file = max_rows_per_file
        self.logger = logger

    ##TODO MAKE STRATEGY_NAME OPTIONAL
    def has_existing_results(
        self, stage: PipelineStage, strategy_name: str, symbol: str
    ) -> bool:
        """
        Check if results already exist for the given stage, strategy, and symbol.
        This is useful to avoid overwriting existing results.
        """
        search_dir = self._get_stage_symbol_dir(stage, symbol)
        pattern = str(search_dir / f"{strategy_name}_{symbol}_*.csv")
        return len(glob.glob(pattern)) > 0

    ##TODO MAKE STRATEGY_NAME OPTIONAL
    def save_stage_data(
        self,
        stage: PipelineStage,
        strategy_name: str,
        symbol: str,
        results_df: pd.DataFrame,
        timestamp: Optional[datetime] = None,
    ) -> list[str]:
        """
        Save the results DataFrame to CSV files, splitting if necessary.
        """
        if results_df is None:
            raise ValueError("None DataFrame provided")
        if not isinstance(results_df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(results_df)}")

        timestamp = timestamp or datetime.now()
        output_dir = self._get_stage_symbol_dir(stage, symbol)
        output_dir.mkdir(parents=True, exist_ok=True)

        if "strategy" not in results_df.columns:
            results_df = results_df.assign(strategy=strategy_name)
        if "symbol" not in results_df.columns:
            results_df = results_df.assign(symbol=symbol)

        total_rows = len(results_df)
        num_parts = ceil(total_rows / self.max_rows_per_file)
        filepaths = []

        for part_idx in range(num_parts):
            chunk_df = results_df.iloc[
                part_idx * self.max_rows_per_file : (part_idx + 1)
                * self.max_rows_per_file
            ]
            part_suffix = f"_part{part_idx + 1}" if num_parts > 1 else ""
            filename = f"{strategy_name}_{symbol}_{timestamp.strftime('%H%M%S')}{part_suffix}.csv"
            filepath = output_dir / filename

            try:
                chunk_df.to_csv(filepath, index=False)
                self.logger.info(f"Saved part {part_idx + 1}/{num_parts} to {filepath}")
                filepaths.append(str(filepath))
            except Exception as e:
                self.logger.error(
                    f"Failed to save chunk {part_idx + 1} for {strategy_name}/{symbol}: {e}"
                )
                raise

        return filepaths

    ##TODO ADD OPTIONAL STRATEGY_NAME
    def _get_stage_symbol_dir(self, stage: PipelineStage, symbol: str) -> Path:
        """Get the directory for a symbol in the stage"""
        return self.pipeline_data_manager.get_directory_path(stage=stage, symbol=symbol)
