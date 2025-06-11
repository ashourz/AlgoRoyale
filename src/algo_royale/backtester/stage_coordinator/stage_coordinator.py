from abc import ABC, abstractmethod
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
        incoming = (
            self.stage.incoming_stage.value if self.stage.incoming_stage else "None"
        )
        outgoing = self.stage.value

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

    async def run(self, load_in_reverse=False) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        self.logger.info(f"Starting stage: {self.stage}")
        if not self.stage.incoming_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            prepared_data = None
        else:
            """ Load data from the incoming stage """
            self.logger.info(f"stage:{self.stage} starting data loading.")
            data = await self._load_data(
                stage=self.stage.incoming_stage, reverse_pages=load_in_reverse
            )
            if not data:
                self.logger.error(
                    f"No data loaded from stage:{self.stage.incoming_stage}"
                )
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
                f"Loading data for stage:{stage} | strategy:{strategy_name}"
            )
            data = await self.data_loader.load_all_stage_data(
                stage=stage, strategy_name=strategy_name, reverse_pages=reverse_pages
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} data loading failed: {e}"
            )
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol="",
                filename="load_data",
                error_message=f"stage:{stage} | strategy:{strategy_name} data loading failed: {e}",
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
                    return self.data_preparer.normalized_stream(
                        stage=stage, symbol=symbol, iterator_factory=df_iter_factory
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

    async def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[
            str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ],  # symbol -> strategy_name -> factory
    ):
        """Write processed data to disk
        This method iterates through the processed data, checks if the data for each symbol and strategy is already marked as done,
        and if not, writes the data to the appropriate directory. If the directory already contains data but is not marked as done,
        it clears the directory before writing the new data. It also handles errors by logging them and writing error files.

        :param stage: The current stage of processing.
        :param processed_data: A dictionary mapping symbols to strategy factories that yield DataFrames.
        :type processed_data: Dict[str, Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]
        """
        self.logger.info(f"Writing data for stage: {stage}")
        try:
            for symbol, strategy_factories in processed_data.items():
                try:
                    self.logger.info(
                        f"Writing data for symbol: {symbol} at stage: {stage}"
                    )
                    for strategy_name, df_iter_factory in strategy_factories.items():
                        try:
                            self.logger.info(
                                f"Processing symbol: {symbol} for strategy: {strategy_name}"
                            )
                            # Check if symbol/stage is already marked as done
                            if self.stage_data_manager.is_symbol_stage_done(
                                stage, strategy_name, symbol
                            ):
                                self.logger.info(
                                    f"Skipping {symbol} for stage:{stage} | strategy:{strategy_name} (already marked as done)"
                                )
                                continue

                            # If folder has data but is not marked as done, clear it
                            out_dir = self.stage_data_manager.get_directory_path(
                                stage, strategy_name, symbol
                            )
                            if out_dir.exists() and any(out_dir.iterdir()):
                                self.logger.info(
                                    f"Clearing existing data for {symbol} at stage:{stage} | strategy:{strategy_name} (not marked as done)"
                                )
                                self.stage_data_manager.clear_directory(
                                    stage, strategy_name, symbol
                                )

                            gen = df_iter_factory()
                            if not hasattr(gen, "__aiter__"):
                                self.logger.error(
                                    f"Factory for {symbol}/{strategy_name} did not return an async iterator. Got: {type(gen)} Value: {gen}"
                                )
                                raise TypeError(
                                    f"Expected async iterator, got {type(gen)}"
                                )

                            # Now write the new data
                            page_idx: int = 1
                            async for df in gen:
                                self.data_writer.save_stage_data(
                                    stage=stage,
                                    strategy_name=strategy_name,
                                    symbol=symbol,
                                    results_df=df,
                                    page_idx=page_idx,
                                )
                                page_idx += 1
                            self.stage_data_manager.mark_symbol_stage(
                                stage=stage,
                                strategy_name=strategy_name,
                                symbol=symbol,
                                statusExtension=DataExtension.DONE,
                            )
                        except Exception as e:
                            self.logger.error(
                                f"stage:{stage} | strategy:{strategy_name} data writing failed for symbol {symbol}: {e}"
                            )
                            self.stage_data_manager.write_error_file(
                                stage=stage,
                                strategy_name=strategy_name,
                                symbol=symbol,
                                filename="write",
                                error_message=f"stage:{stage} | strategy:{strategy_name} data writing failed for symbol {symbol}: {e}",
                            )
                            continue
                except Exception as e:
                    self.logger.error(
                        f"stage:{stage} data writing failed for symbol {symbol}: {e}"
                    )
                    self.stage_data_manager.write_error_file(
                        stage=stage,
                        strategy_name=None,
                        symbol=symbol,
                        filename="write",
                        error_message=f"stage:{stage} data writing failed for symbol {symbol}: {e}",
                    )
                    continue
        except Exception as e:
            self.logger.error(f"stage:{stage} data writing failed: {e}")
            self.stage_data_manager.write_error_file(
                stage=stage,
                strategy_name=None,
                symbol=symbol,
                filename="write",
                error_message=f"stage:{stage} data writing failed: {e}",
            )
            return False
