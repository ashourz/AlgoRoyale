import asyncio
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.i_data_injest.watchlist import load_watchlist
from algo_royale.backtester.pipeline.data_manage.pipeline_data_manager import (
    PipelineDataManager,
)
from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage
from algo_royale.config.config import Config


class StageDataLoader:
    def __init__(
        self, config: Config, logger: Logger, pipeline_data_manager: PipelineDataManager
    ):
        try:
            # Initialize directories and services
            watchlist_path_string = config.get("paths.backtester", "watchlist_path")
            if not watchlist_path_string:
                raise ValueError("Watchlist path not specified in config")
            self.watchlist = load_watchlist(watchlist_path_string)
            # Ensure watchlist is not empty
            if not self.watchlist:
                raise ValueError("Watchlist is empty")

            self.pipeline_data_manager = pipeline_data_manager

            # Initialize logger
            self.logger = logger
            self.logger.info("BacktestDataLoader initialized")

        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize BacktestDataLoader: {e}")

    async def load_all_stage_data(
        self, stage: PipelineStage, strategy_name: Optional[str] = None
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Returns async data generators with automatic data fetching"""
        self.logger.info("Starting async data loading")

        # First ensure we have data for all symbols
        await self._ensure_all_data_exists()

        # Then prepare the async iterators
        data = {}
        for symbol in self.watchlist:
            try:
                # Use functools.partial to properly bind the symbol
                data[symbol] = (
                    lambda s=symbol, st=stage, str=strategy_name: self.load_symbol(
                        stage=st, symbol=s, strategy_name=str
                    )
                )
                self.logger.info(f"Prepared async data loader for: {stage} | {symbol}")
            except Exception as e:
                self.logger.error(
                    f"Failed to prepare loader for {stage} | {symbol}: {str(e)}"
                )
                self.pipeline_data_manager.write_error_file(
                    stage=stage,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    filename="load_all_stage_data",
                    error_message=f"Failed to prepare loader for {stage} | {symbol}: {str(e)}",
                )

        return data

    async def load_symbol(
        self, stage: PipelineStage, symbol: str, strategy_name: Optional[str] = None
    ) -> AsyncIterator[pd.DataFrame]:
        """Async generator yielding DataFrames, fetching data if needed"""
        symbol_dir = self._get_stage_symbol_dir(
            stage=stage, strategy_name=strategy_name, symbol=symbol
        )

        # First ensure we have data
        if not await self._has_existing_data(symbol_dir):
            self.pipeline_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="load_symbol",
                error_message=f"No data available for {stage} | {symbol} | {strategy_name}",
            )
            raise ValueError(
                f"No data available for {stage} | {symbol} | {strategy_name}"
            )

        # Then stream the data
        async for df in self._stream_existing_data_async(
            stage=stage, symbol_dir=symbol_dir
        ):
            yield df

    async def _ensure_all_data_exists(self):
        """
        Ensure that data exists for all symbols in the watchlist for the current stage.
        """
        missing = []
        for symbol in self.watchlist:
            symbol_dir = self._get_stage_symbol_dir(stage=self.stage, symbol=symbol)
            if not self._has_existing_data(symbol_dir):
                missing.append(symbol)
        if missing:
            self.logger.warning(f"Missing data for symbols: {missing}")
            self.pipeline_data_manager.write_error_file(
                stage=self.stage,
                strategy_name=None,
                symbol=symbol,
                filename="_ensure_all_data_exists",
                error_message=f"Missing data for symbols: {missing}",
            )

    def _get_stage_symbol_dir(
        self, stage: PipelineStage, symbol: str, strategy_name: Optional[str] = None
    ) -> Path:
        """Get the directory for a symbol in the stage"""
        return self.pipeline_data_manager.get_directory_path(
            stage=stage, strategy_name=strategy_name, symbol=symbol
        )

    def _has_existing_data(self, symbol_dir: Path) -> bool:
        """Check if valid data exists for a symbol"""
        if not symbol_dir.exists():
            return False
        return any(symbol_dir.iterdir())

    async def _stream_existing_data_async(
        self, stage: PipelineStage, symbol_dir: Path
    ) -> AsyncIterator[pd.DataFrame]:
        """Async generator to stream existing data pages for a symbol"""
        pages = sorted(
            symbol_dir.glob("*.csv"), key=lambda x: int(x.stem.split("_")[-1])
        )

        self.logger.debug(f"Found {len(pages)} data pages in {symbol_dir}")

        for page_path in pages:
            try:
                self.logger.debug(f"Yielding {page_path}")
                # Use to_thread for synchronous file operations
                df = await asyncio.to_thread(
                    pd.read_csv, page_path, parse_dates=["timestamp"]
                )
                yield df
            except Exception as e:
                self.logger.error(f"Error reading {page_path}: {str(e)}")
                self.pipeline_data_manager.write_error_file(
                    stage=stage,
                    strategy_name=None,
                    symbol=page_path.stem.split("_")[0],
                    filename=page_path.name,
                    error_message=f"Error reading {page_path}: {str(e)}",
                )
                continue
