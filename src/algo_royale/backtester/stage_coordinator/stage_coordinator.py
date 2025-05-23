from abc import ABC, abstractmethod
from logging import Logger

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
        logger: Logger,
    ):
        self.stage = stage
        self.config = config
        self.data_loader = data_loader
        self.data_preparer = data_preparer
        self.data_writer = data_writer
        self.logger = logger

    @abstractmethod
    async def process(self, prepared_data: dict) -> dict:
        """
        Process the prepared data for this stage.
        Should return a dict: symbol -> async generator or DataFrame.
        """
        pass

    # TODO: THIS NEEDS TO BE REVIEWED

    async def run(self, strategy_name: str = "default"):
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        data = await self._load_data()
        if not data:
            self.logger.error("No data loaded")
            return False

        prepared_data = self._prepare_data(data)
        if not prepared_data:
            self.logger.error("No data prepared")
            return False

        processed_data = await self.process(prepared_data)
        if not processed_data:
            self.logger.error("Processing failed")
            return False

        await self._write(strategy_name, processed_data)
        self.logger.info(f"{self.stage} stage completed and files saved.")
        return True

    async def _load_data(self) -> dict:
        """Load data based on the configuration"""
        try:
            data = await self.data_loader.load_all_stage_data(stage=self.stage)
            return data
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return False

    def _prepare_data(self, data: dict) -> dict:
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
            self.logger.error(f"Data preparation failed: {e}")
            return False

    async def _write(self, strategy_name: str, processed_data: dict):
        """Write processed data to the stage"""
        for symbol, df_iter_factory in processed_data.items():
            async for df in df_iter_factory():
                self.data_writer.save_stage_data(
                    stage=self.stage,
                    strategy_name=strategy_name,
                    symbol=symbol,
                    results_df=df,
                )
