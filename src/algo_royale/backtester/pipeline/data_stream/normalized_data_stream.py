from logging import Logger

from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage
from algo_royale.backtester.pipeline.data_preparer.data_preparer import DataPreparer


class NormalizedDataStream:
    def __init__(
        self,
        symbol,
        iterator_factory,
        stage: PipelineStage,
        data_preparer: DataPreparer,
        logger: Logger,
    ):
        self.symbol = symbol
        self.iterator_factory = iterator_factory
        self.stage = stage
        self.data_preparer = data_preparer
        self.logger = logger

    async def __aiter__(self):
        iterator = self.iterator_factory()
        try:
            async for df in iterator:
                try:
                    yield self.data_preparer.normalize_dataframe(
                        df=df, stage=self.stage, symbol=self.symbol
                    )
                except Exception as e:
                    self.logger.error(f"Error processing {self.symbol} data: {e}")
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()
