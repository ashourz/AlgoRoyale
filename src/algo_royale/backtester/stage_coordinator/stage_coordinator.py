from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.enum.data_extension import DataExtension
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter


class StageCoordinator(ABC):
    def __init__(
        self,
        stage: BacktestStage,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
    ):
        self.stage = stage
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.data_writer = data_writer
        self.logger = logger
        self.stage_data_manager = stage_data_manager
        incoming = self.stage.input_stage.name if self.stage.input_stage else "None"
        outgoing = self.stage.name

        self.logger.info(f"{incoming} -> {outgoing} StageCoordinator initialized")

    @abstractmethod
    async def process(
        self,
        prepared_data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]],
    ) -> Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Process the prepared data and return a dict mapping symbol to a factory that yields result DataFrames.
        This method should be implemented by subclasses to define the specific processing logic.
        :param prepared_data: Data prepared for processing, typically a dict mapping symbol to an async iterator factory.
        :return: A dict mapping symbol to a dict of strategy names and their corresponding async iterator factories.
        :rtype: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]
        """
        pass

    async def run(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        load_in_reverse=False,
    ) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.window_id = self.stage_data_manager.get_window_id(
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.logger.info(
            f"Starting stage: {self.stage} | start_date: {start_date} | end_date: {end_date}"
        )
        if not self.stage.input_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            prepared_data = None
        else:
            """ Load data from the incoming stage """
            self.logger.info(f"stage:{self.stage} starting data loading.")
            data = await self._load_data(
                stage=self.stage.input_stage, reverse_pages=load_in_reverse
            )
            if not data:
                self.logger.error(f"No data loaded from stage:{self.stage.input_stage}")
                return False

            prepared_data = self._prepare_data(stage=self.stage, data=data)
            if not prepared_data:
                self.logger.error(f"No data prepared for stage:{self.stage}")
                return False

        processed_data = await self.process(prepared_data)

        if not processed_data:
            self.logger.error(f"Processing failed for stage:{self.stage}")
            return False

        await self._write(
            stage=self.stage,
            processed_data=processed_data,
        )
        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True

    async def _load_data(
        self,
        stage: BacktestStage,
        strategy_name: Optional[str] = None,
        reverse_pages: bool = False,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Load data based on the configuration"""
        try:
            self.logger.info(
                f"Loading data for stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date}"
            )
            data = await self.data_loader.load_all_stage_data(
                stage=stage,
                strategy_name=strategy_name,
                start_date=self.start_date,
                end_date=self.end_date,
                reverse_pages=reverse_pages,
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data loading failed: {e}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol="",
                filename="load_data",
                error_message=f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data loading failed: {e}",
                start_date=self.start_date,
                end_date=self.end_date,
            )
            return {}

    def _prepare_data(
        self,
        stage: BacktestStage,
        data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
        strategy_name: Optional[str] = None,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Prepare data for processing"""
        self.logger.info(f"Preparing data for stage:{stage} | strategy:{strategy_name}")
        prepared_data = {}
        for symbol, df_iter_factory in data.items():

            def factory(symbol=symbol, df_iter_factory=df_iter_factory):
                try:
                    self.logger.info(
                        f"Calling factory for {symbol}, df_iter_factory={df_iter_factory}"
                    )
                    return self.data_preparer.normalize_stream(
                        iterator_factory=df_iter_factory
                    )
                except Exception as e:
                    self.logger.error(
                        f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}"
                    )
                    self.stage_data_manager.write_error_file(
                        stage=stage,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        filename="prepare_data",
                        error_message=f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}",
                    )
                    raise

            prepared_data[symbol] = factory
        self.logger.info(
            f"Data prepared for stage:{stage} | strategy:{strategy_name} with {len(prepared_data)} symbols"
        )
        return prepared_data

    async def _write_(
        self,
        stage: BacktestStage,
        processed_data: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]],
    ):
        """Write processed data to disk."""
        self.logger.info(f"Writing data for stage: {stage}")
        try:
            for symbol, strategy_factories in processed_data.items():
                await self._write_symbol_data(stage, symbol, strategy_factories)
        except Exception as e:
            self._handle_global_write_error(stage, e)
            return False

    async def _write_symbol_data(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_factories: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
    ):
        """Write data for a specific symbol."""
        try:
            self.logger.info(f"Writing data for symbol: {symbol} at stage: {stage}")
            for strategy_name, df_iter_factory in strategy_factories.items():
                await self._write_strategy_data(
                    stage, symbol, strategy_name, df_iter_factory
                )
        except Exception as e:
            self._handle_symbol_write_error(stage, symbol, e)

    async def _write_strategy_data(
        self,
        stage: BacktestStage,
        symbol: str,
        strategy_name: str,
        df_iter_factory: Callable[[], AsyncIterator[pd.DataFrame]],
    ):
        """Write data for a specific strategy."""
        try:
            if self.stage_data_manager.is_symbol_stage_done(
                stage, strategy_name, symbol, self.start_date, self.end_date
            ):
                self.logger.info(
                    f"Skipping {symbol} for stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} (already marked as done)"
                )
                return

            self._clear_existing_data_if_needed(stage, strategy_name, symbol)

            gen = df_iter_factory()
            if not hasattr(gen, "__aiter__"):
                raise TypeError(f"Expected async iterator, got {type(gen)}")

            await self._write_pages(stage, strategy_name, symbol, gen)
            self.stage_data_manager.mark_symbol_stage(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                statusExtension=DataExtension.DONE,
                start_date=self.start_date,
                end_date=self.end_date,
            )
        except Exception as e:
            self._handle_strategy_write_error(stage, strategy_name, symbol, e)

    async def _write_pages(
        self,
        stage: BacktestStage,
        strategy_name: str,
        symbol: str,
        gen: AsyncIterator[pd.DataFrame],
    ):
        """Write pages of data for a strategy."""
        page_idx = 1
        async for df in gen:
            self.data_writer.save_stage_data(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                results_df=df,
                page_idx=page_idx,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            page_idx += 1

    def _clear_existing_data_if_needed(
        self, stage: BacktestStage, strategy_name: str, symbol: str
    ):
        """Clear existing data if the directory is not marked as done."""
        out_dir = self.stage_data_manager.get_directory_path(
            stage, strategy_name, symbol, self.start_date, self.end_date
        )
        if out_dir.exists() and any(out_dir.iterdir()):
            self.logger.info(
                f"Clearing existing data for {symbol} at stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date}"
            )
            self.stage_data_manager.clear_directory(
                stage, strategy_name, symbol, self.start_date, self.end_date
            )

    def _handle_global_write_error(self, stage: BacktestStage, e: Exception):
        """Handle errors during the global write process."""
        self.logger.error(f"stage:{stage} data writing failed: {e}")
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=None,
            symbol="",
            filename="write",
            error_message=f"stage:{stage} data writing failed: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def _handle_symbol_write_error(
        self, stage: BacktestStage, symbol: str, e: Exception
    ):
        """Handle errors during the symbol write process."""
        self.logger.error(f"stage:{stage} data writing failed for symbol {symbol}: {e}")
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=None,
            symbol=symbol,
            filename="write",
            error_message=f"stage:{stage} data writing failed for symbol {symbol}: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def _handle_strategy_write_error(
        self, stage: BacktestStage, strategy_name: str, symbol: str, e: Exception
    ):
        """Handle errors during the strategy write process."""
        self.logger.error(
            f"stage:{stage} | strategy:{strategy_name} | start_date:{self.start_date} | end_date:{self.end_date} data writing failed for symbol {symbol}: {e}"
        )
        self.stage_data_manager.write_error_file(
            stage=stage,
            strategy_name=strategy_name,
            symbol=symbol,
            filename="write",
            error_message=f"stage:{stage} | strategy:{strategy_name} data writing failed for symbol {symbol}: {e}",
            start_date=self.start_date,
            end_date=self.end_date,
        )
