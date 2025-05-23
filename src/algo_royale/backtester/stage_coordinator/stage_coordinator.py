from abc import ABC, abstractmethod
from logging import Logger
from typing import AsyncIterator, Callable, Dict, Optional

import pandas as pd

from algo_royale.backtester.pipeline.data_manage.pipeline_data_manager import (
    PipelineDataManager,
)
from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage
from algo_royale.backtester.pipeline.data_manage.stage_data_loader import (
    StageDataLoader,
)
from algo_royale.backtester.pipeline.data_manage.stage_data_writer import (
    StageDataWriter,
)
from algo_royale.backtester.pipeline.data_preparer.async_data_preparer import (
    AsyncDataPreparer,
)


class StageCoordinator(ABC):
    def __init__(
        self,
        stage: PipelineStage,
        config: dict,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        pipeline_data_manager: PipelineDataManager,
        logger: Logger,
    ):
        self.stage = stage
        self.config = config
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.data_writer = data_writer
        self.logger = logger
        self.pipeline_data_manager = pipeline_data_manager
        self.logger.info(f"StageCoordinator for {self.stage} initialized")

    @abstractmethod
    async def process(
        self, prepared_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
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
        data = await self._load_data(strategy_name=strategy_name)
        if not data:
            self.logger.error("No data loaded")
            return False

        prepared_data = self._prepare_data(data=data, strategy_name=strategy_name)
        if not prepared_data:
            self.logger.error("No data prepared")
            return False

        processed_data = await self.process(prepared_data)
        if not processed_data:
            self.logger.error("Processing failed")
            return False

        await self._write(processed_data=processed_data, strategy_name=strategy_name)
        self.logger.info(
            f"stage:{self.stage} | strategy:{strategy_name} completed and files saved."
        )
        return True

    async def _load_data(
        self, strategy_name: Optional[str] = None
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """Load data based on the configuration"""
        try:
            data = await self.data_loader.load_all_stage_data(
                stage=self.stage, strategy_name=strategy_name
            )
            return data
        except Exception as e:
            self.logger.error(
                f"stage:{self.stage} | strategy:{strategy_name} data loading failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
                stage=self.stage,
                strategy_name=strategy_name,
                symbol="",
                filename="load_data",
                error_message=f"stage:{self.stage} | strategy:{strategy_name} data loading failed: {e}",
            )
            return {}

    def _prepare_data(
        self,
        data: Dict[str, Callable[[], AsyncIterator]],
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
                f"stage:{self.stage} | strategy:{strategy_name} data preparation failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
                stage=self.stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="prepare_data",
                error_message=f"stage:{self.stage} | strategy:{strategy_name} data preparation failed: {e}",
            )
            return {}

    async def _write(
        self,
        processed_data: Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]],
        strategy_name: Optional[str] = None,
    ):
        """Write processed data to the stage"""
        try:
            for symbol, df_iter_factory in processed_data.items():
                async for df in df_iter_factory():
                    self.data_writer.save_stage_data(
                        stage=self.stage,
                        strategy_name=strategy_name,
                        symbol=symbol,
                        results_df=df,
                    )
        except Exception as e:
            self.logger.error(
                f"stage:{self.stage} | strategy:{strategy_name} data writing failed: {e}"
            )
            self.pipeline_data_manager.write_error_file(
                stage=self.stage,
                strategy_name=strategy_name,
                symbol=symbol,
                filename="write",
                error_message=f"stage:{self.stage} | strategy:{strategy_name} data writing failed: {e}",
            )
            return False
