from algo_royale.backtester.pipeline.data_stream.normalized_data_stream import NormalizedDataStream


class NormalizedDataStreamFactory:
    def __init__(self, data_preparer, logger):
        self.data_preparer = data_preparer
        self.logger = logger

    def create(self, symbol, iterator_factory, config):
        return NormalizedDataStream(symbol, iterator_factory, config, self.data_preparer, self.logger)