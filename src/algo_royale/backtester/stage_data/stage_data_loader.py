import asyncio
import re
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager


class StageDataLoader:
    def __init__(
        self,
        logger: Logger,
        stage_data_manager: StageDataManager,
        load_watchlist: Callable[[str], list[str]],
        watchlist_path_string: str,
    ):
        try:
            self.load_watchlist = load_watchlist
            self.watchlist_path = watchlist_path_string
            self.stage_data_manager = stage_data_manager

            # Initialize logger
            self.logger = logger
            self.logger.info("BacktestDataLoader initialized")
            if not self.watchlist_path:
                raise RuntimeError("Watchlist path not specified in config")
            watchlist = self.get_watchlist()
            if not watchlist:
                raise RuntimeError("Watchlist is empty")
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize BacktestDataLoader: {e}")

    def get_watchlist(self):
        """
        Load the watchlist from the specified path.
        """
        return self.load_watchlist(self.watchlist_path)

    async def load_all_stage_data(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        reverse_pages: bool = False,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Returns async data generators with automatic data fetching
        for all symbols in the watchlist for the given stage and strategy.

        This method prepares async generators for each symbol in the watchlist
        that has existing data for the specified stage and strategy.
        If no data exists for a symbol, it will log an error and skip that symbol.

        Args:
            stage (BacktestStage): The stage for which to load data.
            strategy_name (Optional[str]): The name of the strategy, if applicable.

        Returns:
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]: A dictionary
            mapping symbols to async generators that yield DataFrames.

        """
        self.logger.info("Starting async data loading")

        # First ensure we have data for all symbols
        existing_symbols = await self._get_all_existing_data_symbols(
            stage=stage,
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
        )
        if not existing_symbols:
            self.logger.error(
                f"No existing data found for stage: {stage} | strategy: {strategy_name}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=None,
                filename="load_all_stage_data",
                error_message=f"No existing data found for stage: {stage} | strategy: {strategy_name}",
            )
            return {}
        # Then prepare the async iterators
        data = {}
        for symbol in existing_symbols:
            # Skip if symbol is not in watchlist
            if symbol not in self.get_watchlist():
                self.logger.warning(
                    f"Symbol {symbol} not in watchlist, skipping for stage: {stage} | strategy: {strategy_name}"
                )
                continue
            try:
                # Prepare the async generator for the symbol
                data[symbol] = (
                    lambda s=symbol, st=stage, str=strategy_name: self._symbol_data_gen(
                        stage=st,
                        symbol=s,
                        strategy_name=str,
                        reverse_pages=reverse_pages,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

                self.logger.info(f"Prepared async data loader for: {stage} | {symbol}")
            except Exception as e:
                self.logger.error(
                    f"Failed to prepare loader for {stage} | {symbol}: {str(e)}"
                )
                self.stage_data_manager.write_error_file(
                    stage=stage,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    filename="load_all_stage_data",
                    error_message=f"Failed to prepare loader for {stage} | {symbol}: {str(e)}",
                )

        return data

    def _symbol_data_gen(
        self,
        stage,
        symbol,
        strategy_name,
        reverse_pages=False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ):
        async def gen():
            async for df in self.load_symbol(
                stage,
                symbol=symbol,
                strategy_name=strategy_name,
                reverse_pages=reverse_pages,
                start_date=start_date,
                end_date=end_date,
            ):
                yield df

        return gen()

    async def load_symbol(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_name: Optional[str] = None,
        reverse_pages: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AsyncIterator[pd.DataFrame]:
        """Async generator yielding DataFrames, fetching data if needed"""
        symbol_dir = self._get_stage_symbol_dir(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        # First ensure we have data
        if not self._has_existing_data(symbol_dir):
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="load_symbol",
                error_message=f"No data available for {stage} | {symbol} | {strategy_name}",
                start_date=start_date,
                end_date=end_date,
            )
            raise ValueError(
                f"No data available for {stage} | {symbol} | {strategy_name}"
            )

        # Then stream the data
        async for df in self._stream_existing_data_async(
            stage=stage,
            strategy_name=strategy_name,
            symbol_dir=symbol_dir,
            reverse_pages=reverse_pages,
        ):
            yield df

    async def _get_all_existing_data_symbols(
        self,
        stage: BacktestStage,
        strategy_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[str]:
        """
        Ensure that data exists for all symbols in the watchlist for the current stage.
        This method checks each symbol in the watchlist and returns a list of symbols
        that have valid data for the specified stage and strategy.
        Returns a list of symbols that have valid data.
        """
        not_done = []
        missing = []
        done = []
        for symbol in self.get_watchlist():
            symbol_dir = self._get_stage_symbol_dir(
                stage=stage,
                symbol=symbol,
                strategy_name=strategy_name,
                start_date=start_date,
                end_date=end_date,
            )
            if not self._has_existing_data(symbol_dir):
                missing.append(symbol)
            elif not self.stage_data_manager.is_symbol_stage_done(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            ):
                not_done.append(symbol)
            else:
                done.append(symbol)

        if missing:
            # Log and write an error if any symbols are missing data
            self.logger.warning(
                f"Missing data for symbols: {missing} in directory. stage: {stage} | strategy: {strategy_name}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="_ensure_all_data_exists",
                error_message=f"Missing data for symbols: {missing} in directory. stage: {stage} | strategy: {strategy_name}",
                start_date=start_date,
                end_date=end_date,
            )

        if not_done:
            # Log and write an error if any symbols are not marked as done
            self.logger.warning(
                f"Symbols not marked as done: {not_done} in directory. stage: {stage} | strategy: {strategy_name}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="_ensure_all_data_exists",
                error_message=f"Symbols not marked as done: {not_done} in directory. stage: {stage} | strategy: {strategy_name}",
                start_date=start_date,
                end_date=end_date,
            )

        return done

    def _get_stage_symbol_dir(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Path:
        """Get the directory for a symbol in the stage"""
        return self.stage_data_manager.get_directory_path(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

    def _has_existing_data(self, symbol_dir: Path) -> bool:
        """Check if valid data exists for a symbol"""
        if not symbol_dir.exists():
            return False
        return any(symbol_dir.iterdir())

    async def _stream_existing_data_async(
        self,
        stage: BacktestStage,
        strategy_name: str,
        symbol_dir: Path,
        reverse_pages: bool = False,
    ) -> AsyncIterator[pd.DataFrame]:
        """Async generator to stream existing data pages for a symbol"""

        def extract_page_chunk(filename):
            # Example: None_GOOG_page1_chunk2 or None_GOOG_page1
            m = re.search(r"_page(\d+)(?:_chunk(\d+))?$", filename.stem)
            if m:
                page = int(m.group(1))
                chunk = int(m.group(2)) if m.group(2) else 1
                return (page, chunk)
            return (float("inf"), float("inf"))  # Put unparseable files at the end

        pages = sorted(
            [
                f
                for f in symbol_dir.glob("*.csv")
                if not any(
                    f.name.endswith(f".{ext.value}.csv") for ext in DataExtension
                )
            ],
            key=extract_page_chunk,
            reverse=reverse_pages,  # <-- This is the key line!
        )

        self.logger.debug(f"Found {len(pages)} data pages in {symbol_dir}")

        for page_path in pages:
            try:
                self.logger.debug(f"Yielding {page_path}")
                df = await asyncio.to_thread(
                    pd.read_csv, page_path, parse_dates=["timestamp"]
                )
                yield df
            except Exception as e:
                self.logger.error(f"Error reading {page_path}: {str(e)}")
                self.stage_data_manager.write_error_file(
                    stage=stage,
                    strategy_name=strategy_name,
                    symbol=page_path.stem.split("_")[0],
                    filename=page_path.name,
                    error_message=f"Error reading {page_path}: {str(e)}",
                )
                continue
