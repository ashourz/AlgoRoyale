from algo_royale.backtester.data_preparer.data_preparer import DataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage


class AsyncDataPreparer(DataPreparer):
    def __init__(self, logger):
        super().__init__(logger)

    async def normalized_stream(
        self, stage: BacktestStage, symbol: str, iterator_factory
    ):
        iterator = iterator_factory()
        try:
            async for df in iterator:
                try:
                    yield self.normalize_dataframe(df, stage, symbol)
                except Exception as e:
                    self.logger.error(f"Error processing {symbol} data: {e}")
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()
