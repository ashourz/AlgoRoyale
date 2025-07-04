from datetime import datetime
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.feature_engineering.feature_engineer import (
    FeatureEngineer,
)
from algo_royale.backtester.stage_coordinator.data_staging.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager


class FeatureEngineeringStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: SymbolStrategyDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        feature_engineer: FeatureEngineer,
    ):
        super().__init__(
            stage=BacktestStage.FEATURE_ENGINEERING,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.feature_engineer = feature_engineer
        self.data_writer = data_writer

    async def run(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
                stage=self.stage.input_stage, reverse_pages=True
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
                        stage=stage, iterator_factory=df_iter_factory
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

    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Dict[None, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Process the prepared data for this stage.
        Should return a dict: symbol -> async generator or DataFrame.
        """
        engineered_data = await self._engineer(prepared_data)
        if not engineered_data:
            self.logger.error("Feature engineering failed")
            return {}
        # Wrap each factory in a dict with None as the strategy name
        return {symbol: {None: factory} for symbol, factory in engineered_data.items()}

    async def _engineer(
        self, ingest_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        engineered = {}
        for symbol, df_iter_factory in ingest_data.items():

            def factory(symbol=symbol, df_iter_factory=df_iter_factory):
                self.logger.info(
                    f"Calling factory for {symbol}, df_iter_factory={df_iter_factory}"
                )
                result = df_iter_factory()
                self.logger.info(
                    f"Result from df_iter_factory for {symbol}: {type(result)}"
                )
                if not hasattr(result, "__aiter__"):
                    self.logger.error(
                        f"df_iter_factory for {symbol} did not return an async iterator. Got: {type(result)} Value: {result}"
                    )
                    raise TypeError(f"Expected async iterator, got {type(result)}")
                return self.feature_engineer.engineer_features(result, symbol)

            engineered[symbol] = factory

        return engineered

    async def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[
            str, Dict[None, Callable[[], AsyncIterator[pd.DataFrame]]]
        ],
    ):
        """Write processed data to disk."""
        return await self.data_writer.write_symbol_strategy_data_factory(
            stage=stage,
            symbol_strategy_data_factory=processed_data,
            start_data=self.start_date,
            end_data=self.end_date,
        )
