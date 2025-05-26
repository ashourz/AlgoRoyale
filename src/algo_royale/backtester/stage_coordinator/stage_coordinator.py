from abc import ABC, abstractmethod
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter


class StageCoordinator(ABC):
    def __init__(
        self,
        stage: BacktestStage,
        config: dict,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        pipeline_data_manager: StageDataManager,
        logger: Logger,
    ):
        self.stage = stage
        self.config = config
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.data_writer = data_writer
        self.logger = logger
        self.pipeline_data_manager = pipeline_data_manager
        self.logger.info(
            f"{self.input_stage} -> {self.output_stage} StageCoordinator initialized"
        )

    @abstractmethod
    async def process(
        self,
        prepared_data: Optional[Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]],
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Process the prepared data for this stage.
        Should return a dict: symbol -> async generator or DataFrame.
        """
        pass

    async def run(self, strategy_name: Optional[str] = None) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        if not self.stage.incoming_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            prepared_data = None
        else:
            """ Load data from the incoming stage """
            self.logger.info(
                f"stage:{self.stage} | strategy:{strategy_name} starting data loading."
            )
            data = await self._load_data(
                stage=self.stage.incoming_stage, strategy_name=strategy_name
            )
            if not data:
                self.logger.error(
                    f"No data loaded from stage:{self.stage.incoming_stage} | strategy:{strategy_name}"
                )
                return False

            prepared_data = self._prepare_data(
                stage=self.stage, data=data, strategy_name=strategy_name
            )
            if not prepared_data:
                self.logger.error(
                    f"No data prepared for stage:{self.stage} | strategy:{strategy_name}"
                )
                return False

        processed_data = await self.process(prepared_data)
        if not processed_data:
            self.logger.error(
                f"Processing failed for stage:{self.stage} | strategy:{strategy_name}"
            )
            return False

        await self._write(
            stage=self.stage,
            processed_data=processed_data,
            strategy_name=strategy_name,
        )
        self.logger.info(
            f"stage:{self.stage} | strategy:{strategy_name} completed and files saved."
        )
        return True

    async def _load_data(
        self, stage: BacktestStage, strategy_name: Optional[str] = None
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Load data based on the configuration"""
        try:
            data = await self.data_loader.load_all_stage_data(
                stage=stage, strategy_name=strategy_name
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} data loading failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
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
        try:
            prepared_data = {}
            for symbol, df_iter_factory in data.items():
                prepared_data[symbol] = (
                    lambda symbol=symbol,
                    df_iter_factory=df_iter_factory: self.data_preparer.normalized_stream(
                        symbol, df_iter_factory, self.config
                    )
                )
            return prepared_data
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="prepare_data",
                error_message=f"stage:{stage} | strategy:{strategy_name} data preparation failed: {e}",
            )
            return {}

    async def _write(
        self,
        stage: BacktestStage,
        processed_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
        strategy_name: Optional[str] = None,
    ):
        """Write processed data to the stage"""
        try:
            for symbol, df_iter_factory in processed_data.items():
                async for df in df_iter_factory():
                    self.data_writer.save_stage_data(
                        stage=stage,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        results_df=df,
                    )
        except Exception as e:
            self.logger.error(
                f"stage:{stage} | strategy:{strategy_name} data writing failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
                stage=stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="write",
                error_message=f"stage:{stage} | strategy:{strategy_name} data writing failed: {e}",
            )
            return False
