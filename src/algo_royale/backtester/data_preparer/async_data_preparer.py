import logging

from algo_royale.backtester.data_preparer.data_preparer import DataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.logging.logger_singleton import mockLogger


class AsyncDataPreparer(DataPreparer):
    def __init__(self, logger):
        super().__init__(logger)

    async def normalize_stream(
        self, stage: BacktestStage, symbol: str, iterator_factory
    ):
        try:
            iterator = iterator_factory()
            self.logger.info(
                f"Result from normalized_stream iterator_factory for {symbol}: {type(iterator)}"
            )
            if not hasattr(iterator, "__aiter__"):
                self.logger.error(
                    f"normalized_stream iterator_factory for {symbol} did not return an async iterator. Got: {type(iterator)} Value: {iterator}"
                )
                raise TypeError(f"Expected async iterator, got {type(iterator)}")
            async for df in iterator:
                try:
                    yield self.validate_dataframe(df, stage, symbol)
                except Exception as e:
                    self.logger.error(f"Error processing {symbol} data: {e}")
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()


def mockAsyncDataPreparer() -> AsyncDataPreparer:
    """Creates a mock AsyncDataPreparer for testing purposes."""

    logger: logging.Logger = mockLogger()
    return AsyncDataPreparer(logger=logger)
