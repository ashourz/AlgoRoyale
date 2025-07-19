from datetime import datetime
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.feature_engineering.feature_engineer import (
    FeatureEngineer,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.writer.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.logging.loggable import Loggable


class FeatureEngineeringStageCoordinator(StageCoordinator):
    """
    Coordinate the feature engineering stage.
    This stage is responsible for loading data, preparing it for feature engineering,
    processing the data to engineer features, and writing the processed data to disk.
    Parameters:
        data_loader: SymbolStrategyDataLoader instance for loading data.
        data_preparer: StageDataPreparer instance for preparing data.
        data_writer: SymbolStrategyDataWriter instance for writing data.
        stage_data_manager: StageDataManager instance for managing stage data.
        logger: Loggable instance for logging information and errors.
        feature_engineer: FeatureEngineer instance for engineering features.
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        data_writer: SymbolStrategyDataWriter,
        stage_data_manager: StageDataManager,
        logger: Loggable,
        feature_engineer: FeatureEngineer,
    ):
        self.stage = BacktestStage.FEATURE_ENGINEERING
        self.data_loader = data_loader
        self.data_writer = data_writer
        self.stage_data_manager = stage_data_manager
        self.logger = logger
        self.feature_engineer = feature_engineer

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
            raise ValueError(
                f"Stage {self.stage} has no incoming stage defined. Cannot proceed with data loading."
            )
        # Load data for the given stage and date range
        self.logger.info(f"stage:{self.stage} starting data loading.")
        data = await self._load_data(
            stage=self.stage.input_stage,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        if not data:
            self.logger.error(f"No data loaded from stage:{self.stage.input_stage}")
            return False

        # Process the prepared data
        self.logger.info(f"stage:{self.stage} starting data processing.")
        processed_data = await self._process(data)

        if not processed_data:
            self.logger.error(f"Processing failed for stage:{self.stage}")
            return False

        # Write the processed data to disk
        self.logger.info(f"stage:{self.stage} starting data writing.")
        await self._write(
            stage=self.stage,
            processed_data=processed_data,
        )
        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True

    async def _load_data(
        self, stage: BacktestStage, start_date: datetime, end_date: datetime
    ) -> Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Load data for the given stage and date range.
        """
        try:
            self.logger.info(
                f"Loading data for stage: {stage} | start_date: {start_date} | end_date: {end_date}"
            )
            data = await self.data_loader.load_data(
                stage=stage,
                start_date=start_date,
                end_date=end_date,
                reverse_pages=True,
                exclude_done_symbols=True,  # Exclude symbols already processed
            )
            if not data:
                self.logger.error(f"No data loaded for stage: {stage}")
                return None

            return data
        except Exception as e:
            self.logger.error(
                f"Error loading data for stage: {stage} | start_date: {start_date} | end_date: {end_date}: {e}"
            )
            return None

    async def _process(
        self, data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
    ) -> Dict[str, Dict[None, Callable[[], AsyncIterator[pd.DataFrame]]]]:
        """
        Process the prepared data for this stage.
        Should return a dict: symbol -> async generator or DataFrame.
        """
        engineered_data = await self._engineer(data)
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
            start_date=self.start_date,
            end_date=self.end_date,
        )
