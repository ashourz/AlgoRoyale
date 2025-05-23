from algo_royale.backtester.pipeline.data_stream.normalized_data_stream import (
    NormalizedDataStream,
)


##TODO: this might be redundant with the data preparer and config validator
class NormalizedDataStreamFactory:
    def __init__(self, data_preparer, logger):
        self.data_preparer = data_preparer
        self.logger = logger

    def create(self, symbol, iterator_factory, stage):
        return NormalizedDataStream(
            symbol, iterator_factory, stage, self.data_preparer, self.logger
        )
