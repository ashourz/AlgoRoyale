from algo_royale.backtester.pipeline.data_preparer.data_preparer import DataPreparer


class AsyncDataPreparer(DataPreparer):
    async def normalized_stream(self, symbol: str, iterator_factory, config: dict):
        iterator = iterator_factory()
        try:
            async for df in iterator:
                try:
                    yield self.normalize_dataframe(df, config, symbol)
                except Exception as e:
                    self.logger.error(f"Error processing {symbol} data: {e}")
        finally:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()
