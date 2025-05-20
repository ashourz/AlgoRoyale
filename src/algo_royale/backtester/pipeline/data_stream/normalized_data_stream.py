class NormalizedDataStream:
    def __init__(self, symbol, iterator_factory, config, data_preparer, logger):
        self.symbol = symbol
        self.iterator_factory = iterator_factory
        self.config = config
        self.data_preparer = data_preparer  # Injected object
        self.logger = logger

    async def __aiter__(self):
        iterator = self.iterator_factory()
        try:
            async for df in iterator:
                try:
                    yield self.data_preparer.normalize_dataframe(df, self.config, self.symbol)
                except Exception as e:
                    self.logger.error(f"Error processing {self.symbol} data: {e}")
        finally:
            if hasattr(iterator, 'aclose'):
                await iterator.aclose()